import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document_template import DocumentTemplate


class TemplateField(BaseModel, table=True):
    __tablename__ = "template_fields"

    template_id: uuid.UUID = Field(foreign_key="document_templates.id", nullable=False)
    name: str = Field(nullable=False)
    description: str

    template: "DocumentTemplate" = Relationship(back_populates="fields")


class TemplateFieldCreate(BaseModel):
    template_id: uuid.UUID
    name: str
    description: str


class TemplateFieldUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class TemplateFieldRead(BaseModel):
    id: uuid.UUID
    template_id: uuid.UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
