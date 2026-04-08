from datetime import datetime

from sqlmodel import Field, SQLModel


class GenerationProcess(SQLModel):
    __tablename__ = "generation_processes"

    id: int | None = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="users.id")
    template_id: int = Field(foreign_key="document_templates.id")
    created_at: datetime = Field(default_factory=datetime.now)


class GeneratedDocument(SQLModel):
    __tablename__ = "generated_documents"

    id: int | None = Field(primary_key=True, default=None)
    gen_process_id: int = Field(foreign_key="generation_processes.id")
    file_path: str
    created_at: datetime = Field(default_factory=datetime.now)
