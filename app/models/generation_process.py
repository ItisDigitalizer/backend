import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document_template import DocumentTemplate
    from app.models.generated_document import GeneratedDocument
    from app.models.user import User


class GenerationProcess(BaseModel, table=True):
    __tablename__ = "generation_processes"

    user_id: uuid.UUID = Field(foreign_key="users.id")
    template_id: uuid.UUID = Field(foreign_key="document_templates.id")

    user: "User" = Relationship(back_populates="processes")
    template: "DocumentTemplate" = Relationship(back_populates="processes")
    documents: List["GeneratedDocument"] = Relationship(back_populates="process")


class GenerationProcessCreate(BaseModel):
    user_id: uuid.UUID
    template_id: uuid.UUID


class GenerationProcessUpdate(BaseModel):
    user_id: uuid.UUID | None = None
    template_id: uuid.UUID | None = None


class GenerationProcessRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    template_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
