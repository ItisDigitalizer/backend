import uuid
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.generation_process import GenerationProcess
    from app.models.template_field import TemplateField
    from app.models.user import User


class DocumentTemplateBase(SQLModel):
    name: str = Field(nullable=False)
    description: str
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    file_path: int


class DocumentTemplate(BaseModel, DocumentTemplateBase, table=True):
    __tablename__ = "document_templates"

    user: "User" = Relationship(back_populates="templates")
    fields: List["TemplateField"] = Relationship(back_populates="template")
    processes: List["GenerationProcess"] = Relationship(back_populates="template")


class DocumentTemplateCreate(DocumentTemplateBase):
    pass


class DocumentTemplateUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    file_path: int | None = None


class DocumentTemplateRead(DocumentTemplateBase, BaseModel):
    pass
