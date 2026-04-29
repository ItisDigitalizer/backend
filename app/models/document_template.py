import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.generation_process import GenerationProcess
    from app.models.template_field import TemplateField
    from app.models.user import User


class DocumentTemplate(BaseModel, table=True):
    __tablename__ = "document_templates"

    name: str = Field(nullable=False)
    description: str
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    file_path: int

    user: "User" = Relationship(back_populates="templates")
    fields: List["TemplateField"] = Relationship(back_populates="template")
    processes: List["GenerationProcess"] = Relationship(back_populates="template")


class DocumentTemplateCreate(BaseModel):
    name: str
    description: str
    user_id: uuid.UUID
    file_path: int


class DocumentTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    file_path: int | None = None


class DocumentTemplateRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    user_id: uuid.UUID
    file_path: int
    created_at: datetime
    updated_at: datetime
