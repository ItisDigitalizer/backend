from pydantic import BaseModel
from datetime import datetime


class DocumentTemplate(BaseModel):
    id: int
    name: str
    description: str
    user_id: int
    file_path: int
    created_at: datetime = datetime.now()
    updated_at: datetime


class TemplateField(BaseModel):
    id: int
    template_id: int
    name: str
    description: str
    created_at: datetime = datetime.now()
    updated_at: datetime
