import uuid
from typing import Sequence

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.generated_document import GeneratedDocument
from app.repositories.base import Repository
from app.schemas.generated_document import GeneratedDocumentFilters


class GeneratedDocumentRepository(Repository[GeneratedDocument]):
    model = GeneratedDocument

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_process_id(
        self, gen_process_id: uuid.UUID, offset: int = 0, limit: int = 100
    ) -> Sequence[GeneratedDocument]:
        filters = GeneratedDocumentFilters(gen_process_id=gen_process_id)
        return await self.fetch(filters, offset, limit)

    async def delete_by_process_id(self, gen_process_id: uuid.UUID) -> int:
        filters = GeneratedDocumentFilters(gen_process_id=gen_process_id)
        documents = await self.fetch(filters)
        for doc in documents:
            await self.delete(doc.id)
        return len(documents)

    async def fetch_with_filters(
        self, filters: GeneratedDocumentFilters, offset: int = 0, limit: int = 100
    ) -> Sequence[GeneratedDocument]:
        return await self.fetch(filters, offset, limit)
