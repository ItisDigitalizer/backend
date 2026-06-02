# app/services/auth_service
from datetime import datetime, timezone

from fastapi import BackgroundTasks, Depends, HTTPException, status
from jose import JWTError

from app.auth.password_utils import hash_password, verify_password
from app.auth.security import (
    create_access_token,
    create_action_token,
    create_refresh_token,
    decode_action_token,
    decode_refresh_token,
)
from app.models import RefreshSession
from app.models.user import User, UserCreate
from app.repositories.refresh_session_repo import RefreshSessionRepository
from app.repositories.user_repo import UserRepository
from app.schemas.authentication import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LogoutResponse,
    RefreshSessionFilters,
    ResetPasswordRequest,
    TokenPayload,
    TokenResponse,
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
    ):
        super().__init__(repository)
        self.service = service
        self.refresh_session_repository = refresh_repo

    async def register(self, user_data: UserCreate, background_tasks: BackgroundTasks):
        if await self.repository.get_by_username(user_data.username):
            raise ValueError("Username already taken")

        if await self.repository.get_by_email(user_data.email):
            raise ValueError("Email already registered")

        # 1. Создаем пользователя (убедись, что в UserCreate или в коде создания стоит is_verified=False по умолчанию)
        new_user = await self.service.create_user(user_data)

        # 2. Генерируем токен подтверждения почты
        verify_token = create_action_token(user_id=str(new_user.id), action="verify")
        print(verify_token)
        verify_link = f"http://localhost:8000/api/v1/auth/verify-account?token={verify_token}"

        # 3. Отправляем email в фоне
        # Достаем сессию из репозитория (обычно это self.repository.session или аналогичное поле)
        session = self.repository._session

        EmailService.send_background_email(
            background_tasks=background_tasks,
            session=session,
            email=new_user.email,
            subject="Подтверждение регистрации",
            template_name="verification.html",
            context={"username": new_user.username, "token_link": verify_link},
            user_id=new_user.id,
        )

        return {"detail": "Регистрация успешна. Ссылка для подтверждения отправлена на почту."}

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

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def verify_account(self, token: str):
        """Метод подтверждения аккаунта"""
        try:
            payload = decode_action_token(token)
            if payload.get("action") != "verify":
                raise HTTPException(status_code=400, detail="Неверное действие для данного токена")

            user_id = payload.get("sub")
            users = await self.repository.fetch_with_filters(UserFilters(id=user_id), 0, 1)  # или твой метод get/fetch_by_id
            user = users[0]

            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")

            if user.is_verified:
                return {"detail": "Аккаунт уже подтвержден."}

            user.is_verified = True
            await self.repository.save(user)  # или метод update/save в твоем BaseService
            return {"success": True, "detail": "Аккаунт успешно подтвержден!"}

        except JWTError:
            raise HTTPException(status_code=400, detail="Токен недействителен или истек")

    async def forgot_password(self, data: ForgotPasswordRequest, background_tasks: BackgroundTasks):
        """Метод запроса на восстановление пароля"""
        user = await self.repository.get_by_email(data.email)

        if not user:
            # Безопасность: не раскрываем, зарегистрирован ли email
            return {"detail": "Если email существует, ссылка для сброса отправлена."}

        reset_token = create_action_token(user_id=str(user.id), action="reset_password")
        print(reset_token)
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"  # Обычно ссылка на фронтенд

        session = self.repository._session
        EmailService.send_background_email(
            background_tasks=background_tasks,
            session=session,
            email=user.email,
            subject="Восстановление пароля",
            template_name="password_reset.html",
            context={"username": user.username, "token_link": reset_link},
            user_id=user.id,
        )
        return {"detail": "Инструкции по восстановлению отправлены на вашу почту."}

    async def reset_password(self, data: ResetPasswordRequest):
        """Метод установки нового пароля"""
        try:
            payload = decode_action_token(data.token)
            if payload.get("action") != "reset_password":
                raise HTTPException(status_code=400, detail="Неверное действие для данного токена")

            user_id = payload.get("sub")
            users = await self.repository.fetch_with_filters(UserFilters(id=user_id), 0, 1)  # или твой метод get/fetch_by_id
            user = users[0]

            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")

            # Хэшируем и сохраняем новый пароль
            user.password = hash_password(data.new_password)
            await self.repository.save(user)
            return {"success": True, "detail": "Пароль успешно изменен."}

        except JWTError:
            raise HTTPException(status_code=400, detail="Токен недействителен или истек")

    async def change_password(self, current_user: User, data: ChangePasswordRequest):
        # 1. Проверяем, правильный ли старый пароль ввёл пользователь
        if not verify_password(data.old_password, current_user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный старый пароль")

        # 2. Проверяем, чтобы новый пароль не совпадал со старым (базовая безопасность)
        if data.old_password == data.new_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Новый пароль не должен совпадать со старым")

        # 3. Хешируем новый пароль и обновляем модель
        current_user.password = hash_password(data.new_password)

        # 4. Сохраняем изменения в базу данных
        await self.repository.save(current_user)

        return {"success": True, "detail": "Пароль успешно обновлен"}

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
