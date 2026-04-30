import uuid

from sqlmodel import SQLModel


class TemplateFieldFilters(SQLModel):
    template_id: uuid.UUID | None = None
