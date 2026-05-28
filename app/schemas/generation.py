from uuid import UUID

from sqlmodel import SQLModel


class GenerateResponse(SQLModel):
    process_id: UUID
    download: str
    files: int
