from typing import Optional, Sequence
from uuid import UUID

from loguru import logger

from app.models.generation_process import (
    GenerationProcess,
    GenerationProcessCreate,
    GenerationProcessUpdate,
)
from app.repositories.generation_process_repo import GenerationProcessRepository
from app.schemas.generation_process import GenerationProcessFilters
from app.services.base import BaseService


class GenerationProcessService(BaseService[GenerationProcessRepository]):
    def __init__(self, repository: GenerationProcessRepository):
        super().__init__(repository)

    async def create_process(self, data: GenerationProcessCreate) -> GenerationProcess:
        logger.info(f"Creating generation process for user {data.user_id}")
        return await self.create(data)

    async def get_by_user_id(self, user_id: UUID) -> Sequence[GenerationProcess]:
        return await self.repository.get_by_user_id(user_id)

    async def get_by_template_id(
        self, template_id: UUID
    ) -> Sequence[GenerationProcess]:
        return await self.repository.get_by_template_id(template_id)

    async def update_process(
        self, process_id: UUID, updates: GenerationProcessUpdate
    ) -> Optional[GenerationProcess]:
        process = await self.get(process_id)  # type: ignore
        if not process:
            return None
        return await self.update(process_id, updates)

    async def delete_process(self, process_id: UUID) -> Optional[GenerationProcess]:
        return await self.repository.delete(process_id)

    async def get_filtered_process(
        self, filters: GenerationProcessFilters, offset: int = 0, limit: int = 100
    ) -> Sequence[GenerationProcess]:
        return await self.repository.fetch_with_filters(filters, offset, limit)
