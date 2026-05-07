from typing import Optional, Sequence
from uuid import UUID

from fastapi.params import Depends
from loguru import logger

from app.models.template_field import (
    TemplateField,
    TemplateFieldCreate,
    TemplateFieldUpdate,
)
from app.repositories.template_field_repo import TemplateFieldRepository
from app.schemas.template_field import TemplateFieldFilters
from app.services.base import BaseService


class TemplateFieldService(BaseService[TemplateField, TemplateFieldRepository]):
    def __init__(
        self, repository: TemplateFieldRepository = Depends(TemplateFieldRepository)
    ):
        super().__init__(repository)

    async def create_field(self, data: TemplateFieldCreate) -> TemplateField:
        logger.info(f"Creating field '{data.name}' for template {data.template_id}")
        return await self.create(data)

    async def get_by_template_id(self, template_id: UUID) -> Sequence[TemplateField]:
        return await self.repository.get_by_template_id(template_id)

    async def update_field(
        self, field_id: UUID, updates: TemplateFieldUpdate
    ) -> TemplateField | None:
        field = await self.get(field_id)
        if not field:
            return None
        return await self.update(field_id, updates)

    async def delete_field(self, field_id: UUID) -> Optional[TemplateField]:
        return await self.repository.delete(field_id)

    async def get_filtered_field(
        self, filters: TemplateFieldFilters, offset: int, limit: int
    ) -> Sequence[TemplateField]:
        return await self.repository.fetch_with_filters(filters, offset, limit)
