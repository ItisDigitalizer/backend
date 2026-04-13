from datetime import datetime

from sqlmodel import Field, SQLModel


class DocumentTemplate(SQLModel, table=True):  # type: ignore
    __tablename__ = "document_templates"

    id: int | None = Field(primary_key=True, default=None)
    name: str = Field(nullable=False)
    description: str
    user_id: int = Field(foreign_key="users.id", nullable=False)
    file_path: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime


class TemplateField(SQLModel, table=True):  # type: ignore
    __tablename__ = "template_fields"

    id: int | None = Field(primary_key=True, default=None)
    template_id: int = Field(foreign_key="document_templates.id", nullable=False)
    name: str = Field(nullable=False)
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime
