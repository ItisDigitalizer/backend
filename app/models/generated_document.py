import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.generation_process import GenerationProcess


class GeneratedDocument(BaseModel, table=True):
    __tablename__ = "generated_documents"

    gen_process_id: uuid.UUID = Field(foreign_key="generation_processes.id")
    file_path: str

    process: "GenerationProcess" = Relationship(back_populates="documents")


class GeneratedDocumentBase(SQLModel):
    gen_process_id: uuid.UUID
    file_path: str


class GeneratedDocumentCreate(GeneratedDocumentBase):
    pass


class GeneratedDocumentUpdate(SQLModel):
    file_path: str | None = None


class GeneratedDocumentRead(GeneratedDocumentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
