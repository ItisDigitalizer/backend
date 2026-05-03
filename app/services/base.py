# app/services/base.py
from typing import Generic, Optional, Sequence, TypeVar
from uuid import UUID

from pydantic import BaseModel

from app.repositories.base import Repository

ModelType = TypeVar("ModelType")

RepositoryType = TypeVar("RepositoryType", bound=Repository)


class BaseService(Generic[RepositoryType]):
    def __init__(self, repository: RepositoryType):
        self.repository = repository

    async def get(self, pk: UUID) -> Optional[ModelType]:
        """Получить запись по ID"""
        return await self.repository.get(pk)

    async def fetch(
        self, filters: Optional[BaseModel] = None, offset: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        """Получить список записей с фильтрацией"""
        return await self.repository.fetch(filters, offset, limit)

    async def create(self, data: BaseModel) -> ModelType:
        """Создать новую запись"""
        instance = self.repository.model(**data.model_dump())
        return await self.repository.save(instance)

    async def update(self, pk: UUID, updates: BaseModel) -> Optional[ModelType]:
        """Обновить запись"""
        return await self.repository.update(pk, updates)

    async def get_all(self, offset: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Получить все записи без фильтрации"""
        return await self.repository.fetch(offset=offset, limit=limit)
