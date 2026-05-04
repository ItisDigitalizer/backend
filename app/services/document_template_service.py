from typing import Optional, Sequence
from uuid import UUID

from fastapi.params import Depends
from loguru import logger

from app.models.document_template import (
    DocumentTemplate,
    DocumentTemplateCreate,
    DocumentTemplateUpdate,
)
from app.repositories.document_template_repo import DocumentTemplateRepository
from app.schemas.document_template import DocumentTemplateFilters
from app.services.base import BaseService


class DocumentTemplateService(BaseService[DocumentTemplateRepository]):
    def __init__(
        self,
        repository: DocumentTemplateRepository = Depends(DocumentTemplateRepository),
    ):
        super().__init__(repository)

    async def create_template(self, data: DocumentTemplateCreate) -> DocumentTemplate:
        existing = await self.repository.get_by_name(data.name)
        if existing:
            raise ValueError(f"Template with name '{data.name}' already exists")
        logger.info(f"Creating template: {data.name}")
        return await self.create(data)

    async def get_by_user_id(self, user_id: UUID) -> Sequence[DocumentTemplate]:
        return await self.repository.get_by_user_id(user_id)

    async def get_by_name(self, name: str) -> Optional[DocumentTemplate]:
        return await self.repository.get_by_name(name)

    async def update_template(
        self, template_id: UUID, updates: DocumentTemplateUpdate
    ) -> Optional[DocumentTemplate]:
        template = await self.get(template_id)  # type: ignore
        if not template:
            return None
        return await self.update(template_id, updates)

    async def delete_template(self, template_id: UUID) -> Optional[DocumentTemplate]:
        return await self.repository.delete(template_id)

    async def get_filtered_templates(
        self, filters: DocumentTemplateFilters, offset: int, limit: int
    ) -> Sequence[DocumentTemplate]:
        return await self.repository.fetch_with_filters(filters, offset, limit)
