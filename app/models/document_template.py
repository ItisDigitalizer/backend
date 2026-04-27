import uuid

from sqlmodel import Field

from app.models.base import BaseModel


class DocumentTemplate(BaseModel, table=True):  # type: ignore
    __tablename__ = "document_templates"

    name: str = Field(nullable=False)
    description: str
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    file_path: int
