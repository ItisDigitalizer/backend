import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.generation_process import GenerationProcess


class GeneratedDocument(BaseModel, table=True):
    __tablename__ = "generated_documents"

    gen_process_id: uuid.UUID = Field(foreign_key="generation_processes.id")
    file_path: str

    process: "GenerationProcess" = Relationship(back_populates="documents")


class GeneratedDocumentCreate(BaseModel):
    gen_process_id: uuid.UUID
    file_path: str


class GeneratedDocumentUpdate(BaseModel):
    file_path: str | None = None


class GeneratedDocumentRead(BaseModel):
    id: uuid.UUID
    gen_process_id: uuid.UUID
    file_path: str
    created_at: datetime
    updated_at: datetime
