# app/services/auth_service
from datetime import datetime, timezone

from fastapi import BackgroundTasks, Depends, HTTPException, Request, status
from jose import JWTError

from app.auth.password_utils import hash_password, verify_password
from app.auth.security import (
    create_access_token,
    create_action_token,
    create_refresh_token,
    decode_action_token,
    decode_refresh_token,
)
from app.core.settings import settings
from app.models import RefreshSession
from app.models.user import User, UserCreate
from app.repositories.refresh_session_repo import RefreshSessionRepository
from app.repositories.user_repo import UserRepository
from app.schemas.authentication import (
    ActionSuccessResponse,
    ChangePasswordRequest,
    EmailNotificationResponse,
    ForgotPasswordRequest,
    LogoutResponse,
    RefreshSessionFilters,
    ResetPasswordRequest,
    TokenPayload,
    TokenResponse,
    TokenUserResponse,
)
from app.schemas.user import UserFilters
from app.services.base import BaseService
from app.services.email_service import EmailService
from app.services.user_service import UserService


class AuthService(BaseService[User, UserRepository]):
    def __init__(
        self,
        repository: UserRepository = Depends(),
        service: UserService = Depends(),
        refresh_repo: RefreshSessionRepository = Depends(),
        email_service: EmailService = Depends(),
    ):
        super().__init__(repository)
        self.service = service
        self.refresh_session_repository = refresh_repo
        self.email_service = email_service

    async def register(self, user_data: UserCreate, background_tasks: BackgroundTasks, request: Request):
        if await self.repository.get_by_username(user_data.username):
            raise ValueError("Username already taken")

        if await self.repository.get_by_email(user_data.email):
            raise ValueError("Email already registered")

        new_user = await self.service.create_user(user_data)

        localhost_url = str(request.base_url).rstrip("/")

        verify_token = create_action_token(user_id=str(new_user.id), action="verify")
        verify_link = f"{localhost_url}/api/v1/auth/verify-account?token={verify_token}"

        self.email_service.send_background_email(
            background_tasks=background_tasks,
            email=new_user.email,
            subject="Подтверждение регистрации",
            template_name="verification.html",
            context={"username": new_user.username, "token_link": verify_link},
            user_id=new_user.id,
        )

        return EmailNotificationResponse(detail="Ссылка для подтверждения отправлена на почту.")

    async def login(self, username: str, password: str):
        user = await self.repository.get_by_username(username)

        if not user or not verify_password(password, user.password):
            raise ValueError("Invalid credentials")

        if not getattr(user, "is_verified", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Аккаунт не подтвержден. Пожалуйста, проверьте почту."
            )

        access_token = create_access_token(str(user.id))

        refresh_token, payload = create_refresh_token(str(user.id))

        await self.refresh_session_repository.save(
            RefreshSession(
                user_id=user.id,
                jti=payload.jti,
                expires_at=datetime.fromtimestamp(
                    payload.exp,
                    tz=timezone.utc,
                ),
            )
        )

        return TokenUserResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user,
        )

    async def verify_account(self, token: str):
        try:
            payload = decode_action_token(token)
            if payload.get("action") != "verify":
                raise HTTPException(status_code=400, detail="Неверное действие для данного токена")

            user_id = payload.get("sub")
            users = await self.repository.fetch_with_filters(UserFilters(id=user_id), 0, 1)
            user = users[0]

            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")

            if user.is_verified:
                return ActionSuccessResponse(success=False, detail="Аккаунт уже подтверждён")

            user.is_verified = True
            await self.repository.save(user)
            return ActionSuccessResponse(success=True, detail="Аккаунт успешно подтверждён")

        except JWTError:
            raise HTTPException(status_code=400, detail="Токен недействителен или истек")

    async def forgot_password(self, data: ForgotPasswordRequest, background_tasks: BackgroundTasks):
        user = await self.repository.get_by_email(data.email)

        if not user:
            return EmailNotificationResponse(detail="Если email существует, ссылка для сброса отправлена.")

        frontend_url = settings.frontend.url.rstrip("/")

        reset_token = create_action_token(user_id=str(user.id), action="reset_password")
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"

        self.email_service.send_background_email(
            background_tasks=background_tasks,
            email=user.email,
            subject="Восстановление пароля",
            template_name="password_reset.html",
            context={"username": user.username, "token_link": reset_link},
            user_id=user.id,
        )

        return EmailNotificationResponse(detail="Если email существует, ссылка для сброса отправлена.")

    async def reset_password(self, data: ResetPasswordRequest):
        try:
            payload = decode_action_token(data.token)
            if payload.get("action") != "reset_password":
                raise HTTPException(status_code=400, detail="Неверное действие для данного токена")

            user_id = payload.get("sub")
            users = await self.repository.fetch_with_filters(UserFilters(id=user_id), 0, 1)
            user = users[0]

            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")

            user.password = hash_password(data.new_password)
            await self.repository.save(user)
            return ActionSuccessResponse(success=True, detail="Пароль успешно изменен.")

        except JWTError:
            raise HTTPException(status_code=400, detail="Токен недействителен или истек")

    async def change_password(self, current_user: User, data: ChangePasswordRequest):
        if not verify_password(data.old_password, current_user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный старый пароль")

        if data.old_password == data.new_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Новый пароль не должен совпадать со старым")

        current_user.password = hash_password(data.new_password)

        await self.repository.save(current_user)

        return ActionSuccessResponse(success=True, detail="Пароль успешно обновлен")

    async def refresh_tokens(self, refresh_token: str):
        try:
            payload = decode_refresh_token(refresh_token)
            token_payload = TokenPayload(**payload)

            session = await self.refresh_session_repository.fetch_one(RefreshSessionFilters(jti=token_payload.jti))

            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh session",
                )

            if session.expires_at < datetime.now(timezone.utc):
                raise ValueError("Session expired")

            await self.refresh_session_repository.delete(session.id)

            new_access = create_access_token(token_payload.sub)

            new_refresh, refresh_payload = create_refresh_token(token_payload.sub)

            await self.refresh_session_repository.save(
                RefreshSession(
                    user_id=token_payload.sub,
                    jti=refresh_payload.jti,
                    expires_at=datetime.fromtimestamp(
                        refresh_payload.exp,
                        tz=timezone.utc,
                    ),
                )
            )

            return TokenResponse(
                access_token=new_access,
                refresh_token=new_refresh,
            )

        except JWTError:
            raise ValueError("Invalid refresh token")

    async def logout(self, refresh_token: str | None) -> LogoutResponse:
        if refresh_token:
            try:
                payload = decode_refresh_token(refresh_token)
                token_payload = TokenPayload(**payload)

                session = await self.refresh_session_repository.fetch_one(RefreshSessionFilters(jti=token_payload.jti))

                if session:
                    await self.refresh_session_repository.delete(session.id)

                if not session:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid refresh session",
                    )

            except JWTError:
                pass

        return LogoutResponse(success=True)
