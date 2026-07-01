from typing import Any, Dict
from uuid import UUID

from sqlmodel import SQLModel


class GenerateResponse(SQLModel):
    process_id: UUID
    download: str
    files: int


class ManualDataRequest(SQLModel):
    data: Dict[str, Any]

    class Config:
        json_schema_extra = {"example": {"data": {"name": "Азат", "age": 25, "course": "math"}}}
