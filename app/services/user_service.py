# app/services/user_service.py
from typing import Optional, Sequence
from uuid import UUID

from fastapi.params import Depends
from loguru import logger

from app.models.user import User, UserCreate, UserUpdate
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserFilters
from app.services.base import BaseService


class UserService(BaseService[UserRepository]):
    def __init__(self, repository: UserRepository = Depends(UserRepository)):
        super().__init__(repository)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        return await self.repository.get_by_email(email)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по username"""
        return await self.repository.get_by_username(username)

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
        # user_data.password_hash = hash_password(user_data.password_hash)

        logger.info(f"Creating user: {user_data.username}")
        return await self.create(user_data)

    async def update_user(self, user_id: UUID, updates: UserUpdate) -> Optional[User]:
        """Обновление пользователя с проверками"""
        user = await self.get(user_id)  # type: ignore
        if not user:
            return None

        # Если обновляется email - проверяем уникальность
        if updates.email and updates.email != user.email:
            existing = await self.get_by_email(updates.email)
            if existing:
                raise ValueError(f"Email {updates.email} already taken")

        # Если обновляется username - проверяем уникальность
        if updates.username and updates.username != user.username:
            existing = await self.get_by_username(updates.username)
            if existing:
                raise ValueError(f"Username {updates.username} already taken")

        logger.info(f"Updating user: {user_id}")
        user = await self.update(user_id, updates)
        return user

    async def get_filtered_users(
        self, filters: UserFilters, skip: int, limit: int
    ) -> Sequence[User]:
        """Получение пользователей с фильтрацией"""
        return await self.repository.fetch_with_filters(filters, skip, limit)

    async def delete_user(self, user_id: UUID) -> Optional[User]:
        return await self.repository.delete(user_id)
