from typing import Optional, Sequence
from uuid import UUID

from loguru import logger

from app.repositories.template_field_repo import TemplateFieldRepository
from app.services.base import BaseService
from app.models.template_field import (
    TemplateField,
    TemplateFieldCreate,
    TemplateFieldUpdate,
)


class TemplateFieldService(BaseService[TemplateFieldRepository]):
    def __init__(self, repository: TemplateFieldRepository):
        super().__init__(repository)

    async def create_field(self, data: TemplateFieldCreate) -> TemplateField:
        logger.info(f"Creating field '{data.name}' for template {data.template_id}")
        return await self.create(data)

    async def get_by_template_id(self, template_id: UUID) -> Sequence[TemplateField]:
        return await self.repository.get_by_template_id(template_id)

    async def update_field(
        self, field_id: UUID, updates: TemplateFieldUpdate
    ) -> Optional[TemplateField]:
        field = await self.get(field_id)  # type: ignore
        if not field:
            return None
        return await self.update(field_id, updates)

    async def delete_field(self, field_id: UUID) -> Optional[TemplateField]:
        return await self.repository.delete(field_id)
