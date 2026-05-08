from uuid import UUID

from fastapi import HTTPException

from app.auth.security import *
from app.models.user import UserCreate, User, UserUpdate
from app.schemas.authentication import LoginRequest
from app.services.user_service import UserService


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def register(self, username: str, password: str, email: str):
        hashed = hash_password(password)

        user_data = UserCreate(
            username=username,
            email=email,
            hashed_password=hashed,
        )

        return await self.user_service.create_user(user_data)

    async def login(self, username: str, password: str):
        user = await self.user_service.get_by_username(username)

        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({"sub": str(user.id)})

        return {
            "access_token": token,
            "token_type": "bearer",
        }

    async def get_current_user(self, token: str) -> User:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise ValueError("Invalid token")

        user = await self.user_service.get(user_id)
        if not user:
            raise ValueError("User not found")

        return user

    async def refresh(self, refresh_token: str):
        payload = decode_refresh_token(refresh_token)
        user_id = payload.get("sub")

        new_access = create_access_token({"sub": user_id})
        return {"access_token": new_access}

    async def change_password(
            self,
            user_id: UUID,
            old_password: str,
            new_password: str,
    ) -> None:
        user = await self.user_service.get(user_id)
        if not user:
            raise ValueError("User not found")

        if not verify_password(old_password, user.password):
            raise ValueError("Invalid current password")

        if old_password == new_password:
            raise ValueError("New password must be different")

        new_hashed_password = hash_password(new_password)

        await self.user_service.update_user(
            user_id,
            UserUpdate(password=new_hashed_password)
        )