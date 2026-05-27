# app/services/auth_service
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from jose import JWTError

from app.auth.password_utils import verify_password
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.models import RefreshSession
from app.models.user import User, UserCreate
from app.repositories.refresh_session_repo import RefreshSessionRepository
from app.repositories.user_repo import UserRepository
from app.schemas.authentication import (
    LogoutResponse,
    RefreshSessionFilters,
    TokenPayload,
    TokenResponse,
)
from app.services.base import BaseService
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

    async def register(self, user_data: UserCreate):
        if await self.repository.get_by_username(user_data.username):
            raise ValueError("Username already taken")

        if await self.repository.get_by_email(user_data.email):
            raise ValueError("Email already registered")

        return await self.service.create_user(user_data)

    async def login(self, username: str, password: str):
        user = await self.repository.get_by_username(username)

        if not user or not verify_password(password, user.password):
            raise ValueError("Invalid credentials")

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
