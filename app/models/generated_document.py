import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.generation_process import GenerationProcess


class GeneratedDocumentBase(SQLModel):
    gen_process_id: uuid.UUID = Field(foreign_key="generation_processes.id")
    file_path: str


class GeneratedDocument(BaseModel, GeneratedDocumentBase, table=True):
    __tablename__ = "generated_documents"

    process: "GenerationProcess" = Relationship(back_populates="documents")


class GeneratedDocumentCreate(GeneratedDocumentBase):
    pass


class GeneratedDocumentUpdate(SQLModel):
    file_path: str | None = None


class GeneratedDocumentRead(GeneratedDocumentBase, BaseModel):
    pass
