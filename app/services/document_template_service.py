from pathlib import Path
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


class DocumentTemplateService(
    BaseService[DocumentTemplate, DocumentTemplateRepository]
):
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
        template = await self.get(template_id)
        if not template:
            return None
        return await self.update(template_id, updates)

    async def delete_template(self, template_id: UUID) -> Optional[DocumentTemplate]:
        return await self.repository.delete(template_id)

    async def get_filtered_templates(
        self, filters: DocumentTemplateFilters, offset: int, limit: int
    ) -> Sequence[DocumentTemplate]:
        return await self.repository.fetch_with_filters(filters, offset, limit)

    async def create_template_with_file(
        self, name: str, description: str | None, docx_content: bytes, user_id: UUID
    ) -> DocumentTemplate | None:
        """Полное создание: БД + файл + путь"""

        # 1. Создаём шаблон (UUID генерится)
        data = DocumentTemplateCreate(
            name=name, description=description, user_id=user_id
        )
        template = await self.create_template(data)

        # 2. UUID → файл
        filename = f"{template.id}.docx"
        path = Path("templates/raw") / filename
        path.parent.mkdir(exist_ok=True)

        with open(path, "wb") as f:
            f.write(docx_content)

        # 3. Обновляем путь
        update_data = DocumentTemplateUpdate(file_path=f"templates/raw/{filename}")
        return await self.update_template(template.id, update_data)
