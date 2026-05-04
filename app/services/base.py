# app/services/base.py
from typing import Generic, Optional, Sequence, TypeVar
from uuid import UUID

from fastapi.params import Depends
from pydantic import BaseModel

from app.repositories.base import Repository
from app.schemas.pagination import PaginationParam

ModelType = TypeVar("ModelType")

RepositoryType = TypeVar("RepositoryType", bound=Repository)


class BaseService(Generic[ModelType, RepositoryType]):
    def __init__(self, repository: RepositoryType):
        self.repository = repository

    async def get(self, pk: UUID) -> ModelType | None:
        """Получить запись по ID"""
        return await self.repository.get(pk)

    async def fetch(
        self,
        filters: Optional[BaseModel] = None,
        pagination: PaginationParam = Depends(),
    ) -> Sequence[ModelType]:
        """Получить список записей с фильтрацией"""
        return await self.repository.fetch(filters, pagination.offset, pagination.limit)

    async def create(self, data: BaseModel) -> ModelType:
        """Создать новую запись"""
        instance = self.repository.model(**data.model_dump())
        return await self.repository.save(instance)

    async def update(self, pk: UUID, updates: BaseModel) -> Optional[ModelType]:
        """Обновить запись"""
        return await self.repository.update(pk, updates)

    async def get_all(self, offset: int, limit: int) -> Sequence[ModelType]:
        """Получить все записи без фильтрации"""
        return await self.repository.fetch(offset=offset, limit=limit)
