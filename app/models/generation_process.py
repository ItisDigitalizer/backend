import uuid
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document_template import DocumentTemplate
    from app.models.generated_document import GeneratedDocument
    from app.models.user import User


class GenerationProcessBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="users.id")
    template_id: uuid.UUID = Field(foreign_key="document_templates.id")


class GenerationProcess(BaseModel, GenerationProcessBase, table=True):
    __tablename__ = "generation_processes"

    user: "User" = Relationship(back_populates="processes")
    template: "DocumentTemplate" = Relationship(back_populates="processes")
    documents: List["GeneratedDocument"] = Relationship(back_populates="process")


class GenerationProcessCreate(GenerationProcessBase):
    pass


class GenerationProcessUpdate(SQLModel):
    user_id: uuid.UUID | None = None
    template_id: uuid.UUID | None = None


class GenerationProcessRead(GenerationProcessBase, BaseModel):
    pass
