import uuid
from typing import Sequence

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.generated_document import GeneratedDocument
from app.repositories.base import Repository


class GeneratedDocumentRepository(Repository[GeneratedDocument]):
    model = GeneratedDocument

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_process_id(
        self, gen_process_id: uuid.UUID
    ) -> Sequence[GeneratedDocument]:
        statement = select(self.model).where(
            self.model.gen_process_id == gen_process_id
        )
        result = await self._session.exec(statement)
        return result.all()

    async def delete_by_process_id(self, gen_process_id: uuid.UUID) -> int:
        documents = await self.get_by_process_id(gen_process_id)
        for doc in documents:
            await self.delete(doc.id)
        return len(documents)
