from typing import Sequence
from uuid import UUID

from app.models.template_field import TemplateField
from app.repositories.base import Repository
from app.schemas.template_field import TemplateFieldFilters


class TemplateFieldRepository(Repository[TemplateField]):
    model = TemplateField

    async def get_by_template_id(self, template_id: UUID) -> Sequence[TemplateField]:
        filters = TemplateFieldFilters(template_id=template_id)
        return await self.fetch(filters)

    async def fetch_with_filters(
        self, filters: TemplateFieldFilters, offset: int, limit: int
    ) -> Sequence[TemplateField]:
        return await self.fetch(filters, offset, limit)
