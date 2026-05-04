# app/repositories/base.py
from typing import Generic, Optional, Sequence, TypeVar, cast
from uuid import UUID

from fastapi.params import Depends
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import and_
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class Repository(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self._session = session

    async def get(self, pk: UUID) -> ModelType | None:
        """Получение по ID"""
        result = await self._session.get(self.model, pk)
        return cast(Optional[ModelType], result)

    async def fetch(
        self,
        filters: Optional[PydanticBaseModel] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Sequence[ModelType]:
        """Получение списка с фильтрацией"""
        select_statement = select(self.model)

        if filters is not None:
            filter_conditions = []
            filters_dict = filters.model_dump()
            for key, value in filters_dict.items():
                if not hasattr(self.model, key):
                    continue
                if value is not None:
                    filter_conditions.append(getattr(self.model, key) == value)

            if filter_conditions:
                select_statement = select_statement.where(and_(*filter_conditions))

        if offset is not None:
            select_statement = select_statement.offset(offset)
        if limit is not None:
            select_statement = select_statement.limit(limit)

        entities = await self._session.exec(select_statement)
        return entities.all()

    async def save(self, instance: ModelType) -> ModelType:
        """Сохранение записи"""
        self._session.add(instance)
        await self._session.commit()
        await self._session.refresh(instance)
        return instance

    async def save_all(self, instances: list[ModelType]) -> list[ModelType]:
        """Сохранение нескольких записей"""
        self._session.add_all(instances)
        await self._session.commit()
        for instance in instances:
            await self._session.refresh(instance)
        return instances

    async def delete(self, pk: UUID) -> Optional[ModelType]:
        """Удаление записи"""
        instance = await self.get(pk)
        if instance is None:
            return None
        await self._session.delete(instance)
        await self._session.commit()
        return instance

    async def update(self, pk: UUID, updates: PydanticBaseModel) -> Optional[ModelType]:
        """Обновление записи"""
        instance = await self.get(pk)
        if instance is None:
            return None

        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        return await self.save(instance)
