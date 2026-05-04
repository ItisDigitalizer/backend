from typing import Sequence
from uuid import UUID

from app.models.generation_process import GenerationProcess
from app.repositories.base import Repository
from app.schemas.generation_process import GenerationProcessFilters


class GenerationProcessRepository(Repository[GenerationProcess]):
    model = GenerationProcess

    async def get_by_user_id(self, user_id: UUID) -> Sequence[GenerationProcess]:
        filters = GenerationProcessFilters(user_id=user_id)
        return await self.fetch(filters)

    async def get_by_template_id(
        self, template_id: UUID
    ) -> Sequence[GenerationProcess]:
        filters = GenerationProcessFilters(template_id=template_id)
        return await self.fetch(filters)

    async def fetch_with_filters(
        self, filters: GenerationProcessFilters, offset: int, limit: int
    ) -> Sequence[GenerationProcess]:
        return await self.fetch(filters, offset, limit)
