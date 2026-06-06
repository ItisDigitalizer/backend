from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import joinedload
from sqlmodel import and_, select

from app.models.generation_process import GenerationProcess
from app.repositories.base import Repository
from app.schemas.generation_process import GenerationProcessFilters


class GenerationProcessRepository(Repository[GenerationProcess]):
    model = GenerationProcess

    async def get_by_user_id(self, user_id: UUID) -> Sequence[GenerationProcess]:
        filters = GenerationProcessFilters(user_id=user_id)
        return await self.fetch(filters)

    async def get_by_template_id(self, template_id: UUID) -> Sequence[GenerationProcess]:
        filters = GenerationProcessFilters(template_id=template_id)
        return await self.fetch(filters)

    async def fetch_with_filters(self, filters: GenerationProcessFilters, offset: int, limit: int) -> Sequence[GenerationProcess]:
        return await self.fetch(filters, offset, limit)

    async def fetch_with_template(
        self,
        filters: GenerationProcessFilters | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Sequence[GenerationProcess]:
        """Получение списка с фильтрацией + подгрузка template"""
        select_statement = select(self.model).options(joinedload(getattr(self.model, "template")))

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

        result = await self._session.exec(select_statement)
        return result.unique().all()
