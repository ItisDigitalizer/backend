from typing import Optional, Sequence
from uuid import UUID


from app.models.document_template import DocumentTemplate
from app.repositories.base import Repository
from app.schemas.document_template import DocumentTemplateFilters


class DocumentTemplateRepository(Repository[DocumentTemplate]):
    model = DocumentTemplate

    async def get_by_user_id(self, user_id: UUID) -> Sequence[DocumentTemplate]:
        filters = DocumentTemplateFilters(user_id=user_id)
        return await self.fetch(filters)

    async def get_by_name(self, name: str) -> Optional[DocumentTemplate]:
        filters = DocumentTemplateFilters(name=name)
        result = await self.fetch(filters)
        return result[0] if result else None

    async def fetch_with_filters(
        self, filters: DocumentTemplateFilters, offset: int, limit: int
    ) -> Sequence[DocumentTemplate]:
        return await self.fetch(filters, offset, limit)
