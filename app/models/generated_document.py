import uuid

from sqlmodel import Field

from app.models.base import BaseModel


class GeneratedDocument(BaseModel, table=True):  # type: ignore
    __tablename__ = "generated_documents"

    gen_process_id: uuid.UUID = Field(foreign_key="generation_processes.id")
    file_path: str
