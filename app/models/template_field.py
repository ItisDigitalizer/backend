import uuid

from sqlmodel import Field

from app.models.base import BaseModel


class TemplateField(BaseModel, table=True):  # type: ignore
    __tablename__ = "template_fields"

    template_id: uuid.UUID = Field(foreign_key="document_templates.id", nullable=False)
    name: str = Field(nullable=False)
    description: str
