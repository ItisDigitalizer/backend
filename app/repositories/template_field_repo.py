from typing import Sequence
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.template_field import TemplateFieldFilters
from app.models.template_field import TemplateField
from app.repositories.base import Repository


class TemplateFieldRepository(Repository[TemplateField]):
    model = TemplateField

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_template_id(self, template_id: UUID) -> Sequence[TemplateField]:
        filters = TemplateFieldFilters(template_id=template_id)
        return await self.fetch(filters)

    async def fetch_with_filters(
        self, filters: TemplateFieldFilters, offset: int = 0, limit: int = 100
    ) -> Sequence[TemplateField]:
        return await self.fetch(filters, offset, limit)
