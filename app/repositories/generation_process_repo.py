from typing import Sequence
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.generation_process import GenerationProcess
from app.repositories.base import Repository


class GenerationProcessRepository(Repository[GenerationProcess]):
    model = GenerationProcess

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user_id(self, user_id: UUID) -> Sequence[GenerationProcess]:
        statement = select(self.model).where(self.model.user_id == user_id)
        result = await self._session.exec(statement)
        return result.all()

    async def get_by_template_id(
        self, template_id: UUID
    ) -> Sequence[GenerationProcess]:
        statement = select(self.model).where(self.model.template_id == template_id)
        result = await self._session.exec(statement)
        return result.all()
