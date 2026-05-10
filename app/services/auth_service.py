#app/services/auth_service
from uuid import UUID

from fastapi import Depends

from app.auth.password_utils import verify_password
from app.auth.security import *
from app.models import RefreshSession
from app.models.user import User, UserCreate
from app.repositories.refresh_session_repo import RefreshSessionRepository
from app.repositories.user_repo import UserRepository
from app.services.base import BaseService
from app.services.user_service import UserService


class AuthService(BaseService[User, UserRepository]):
        def __init__(self,
                repo: UserRepository = Depends(),
                service: UserService = Depends(),
                refresh_repo: RefreshSessionRepository = Depends(),
        ):
            self.repository = repo
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

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

        async def refresh_tokens(self, refresh_token: str):
            try:
                payload = decode_refresh_token(refresh_token)

                jti = payload["jti"]
                user_id = payload["sub"]

                session = await self.refresh_session_repository.get_by_jti(jti)

                if not session:
                    raise ValueError("Session not found")

                if getattr(session, "is_revoked", False):
                    raise ValueError("Session revoked")

                if session.expires_at < datetime.utcnow():
                    raise ValueError("Session expired")

                await self.refresh_session_repository.delete(session.id)

                new_access = create_access_token(user_id)
                new_refresh, refresh_payload = create_refresh_token(user_id)

                await self.refresh_session_repository.save(
                    RefreshSession(
                        user_id=user_id,
                        jti=refresh_payload.jti,
                        expires_at=datetime.fromtimestamp(refresh_payload.exp),
                    )
                )

                return {
                    "access_token": new_access,
                    "refresh_token": new_refresh,
                }

            except JWTError:
                raise ValueError("Invalid refresh token")

        async def logout(self, refresh_token: str):
            try:
                print("RAW TOKEN REPR:", repr(refresh_token))

                payload = decode_refresh_token(refresh_token)

                jti = payload.get("jti")

                if not jti:
                    raise ValueError("Invalid token")

                session = await self.refresh_session_repository.get_by_jti(jti)

                if session:
                    await self.refresh_session_repository.delete(session.id)

            except JWTError:
                raise ValueError("Invalid token")