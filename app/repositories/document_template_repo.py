from typing import Optional, Sequence
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.document_template import DocumentTemplate
from app.repositories.base import Repository


class DocumentTemplateRepository(Repository[DocumentTemplate]):
    model = DocumentTemplate

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user_id(self, user_id: UUID) -> Sequence[DocumentTemplate]:
        statement = select(self.model).where(self.model.user_id == user_id)
        result = await self._session.exec(statement)
        return result.all()

    async def get_by_name(self, name: str) -> Optional[DocumentTemplate]:
        statement = select(self.model).where(self.model.name == name)
        result = await self._session.exec(statement)
        return result.first()
