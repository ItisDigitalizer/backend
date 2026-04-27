import uuid

from sqlmodel import Field

from app.models.base import BaseModel


class GenerationProcess(BaseModel, table=True):  # type: ignore
    __tablename__ = "generation_processes"

    user_id: uuid.UUID = Field(foreign_key="users.id")
    template_id: uuid.UUID = Field(foreign_key="document_templates.id")
