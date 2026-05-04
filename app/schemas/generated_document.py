import uuid

from sqlmodel import SQLModel


class GeneratedDocumentFilters(SQLModel):
    gen_process_id: uuid.UUID | None = None
