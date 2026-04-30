import uuid

from sqlmodel import SQLModel


class DocumentTemplateFilters(SQLModel):
    user_id: uuid.UUID | None = None
    name: str | None = None
