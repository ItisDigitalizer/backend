from typing import Optional, Sequence
from uuid import UUID

from fastapi.params import Depends
from loguru import logger

from app.models.generated_document import (
    GeneratedDocument,
    GeneratedDocumentCreate,
    GeneratedDocumentUpdate,
)
from app.repositories.generated_document_repo import GeneratedDocumentRepository
from app.schemas.generated_document import GeneratedDocumentFilters
from app.services.base import BaseService


class GeneratedDocumentService(
    BaseService[GeneratedDocument, GeneratedDocumentRepository]
):
    def __init__(
        self,
        repository: GeneratedDocumentRepository = Depends(GeneratedDocumentRepository),
    ):
        super().__init__(repository)

    async def create_document(
        self, document_data: GeneratedDocumentCreate
    ) -> GeneratedDocument:
        logger.info(f"Creating document for process: {document_data.gen_process_id}")
        return await self.create(document_data)

    async def get_by_process_id(
        self, gen_process_id: UUID, offset, skip
    ) -> Sequence[GeneratedDocument]:
        return await self.repository.get_by_process_id(gen_process_id, offset, skip)

    async def update_document(
        self, document_id: UUID, updates: GeneratedDocumentUpdate
    ) -> Optional[GeneratedDocument]:
        document = await self.get(document_id)
        if not document:
            return None

        logger.info(f"Updating document: {document_id}")
        return await self.update(document_id, updates)

    async def delete_document(self, document_id: UUID) -> Optional[GeneratedDocument]:
        return await self.repository.delete(document_id)

    async def delete_by_process_id(self, gen_process_id: UUID) -> int:
        return await self.repository.delete_by_process_id(gen_process_id)

    async def get_filtered_document(
        self, filters: GeneratedDocumentFilters, offset: int, limit: int
    ) -> Sequence[GeneratedDocument]:
        return await self.repository.fetch_with_filters(filters, offset, limit)
