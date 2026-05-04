import uuid

from sqlmodel import SQLModel


class GenerationProcessFilters(SQLModel):
    user_id: uuid.UUID | None = None
    template_id: uuid.UUID | None = None
