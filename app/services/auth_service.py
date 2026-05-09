from typing import Optional

from loguru import logger

from app.auth.security import *
from app.models.user import User
from app.repositories.auth_repo import AuthUserRepository
from app.schemas.authentication import UserCreate
from app.services.base import BaseService


class AuthService(BaseService[User, AuthUserRepository]):
        def __init__(self, repo: AuthUserRepository):
            self.repository = repo

        async def register(self, username: str, email: str, password: str):

            if await self.repository.get_by_username(username):
                raise ValueError("Username already taken")

            if await self.repository.get_by_email(email):
                raise ValueError("Email already registered")

            return await self.create_user(user_data=UserCreate(username=username, password=password, email=email))


        async def login(self, username: str, password: str):
            user = await self.repository.get_by_username(username)

            if not user or not verify_password(password, user.password):
                raise ValueError("Invalid credentials")

            token = create_access_token({"sub": str(user.id)})

            return {
                "access_token": token,
                "token_type": "bearer",
            }

        async def change_password(self, user_id, old_password, new_password):
            user = await self.repository.get_by_id(user_id)

            if not user:
                raise ValueError("User not found")

            if not verify_password(old_password, user.password):
                raise ValueError("Invalid password")

            user.password = hash_password(new_password)

            await self.repository.update(user)

        async def create_user(self, user_data: UserCreate) -> User:
            """Создание пользователя с проверкой уникальности"""
            # Проверка email
            existing_email = await self.get_by_email(user_data.email)
            if existing_email:
                raise ValueError(f"User with email {user_data.email} already exists")

            # Проверка username
            existing_username = await self.get_by_username(user_data.username)
            if existing_username:
                raise ValueError(f"User with username {user_data.username} already exists")

            # Здесь должен быть хеширование пароля
            user_data.password = hash_password(user_data.password)

            logger.info(f"Creating user: {user_data.username}")
            return await self.create(user_data)

        async def get_by_email(self, email: str) -> Optional[User]:
            """Получение пользователя по email"""
            return await self.repository.get_by_email(email)

        async def get_by_username(self, username: str) -> Optional[User]:
            """Получение пользователя по username"""
            return await self.repository.get_by_username(username)