from pydantic import BaseModel
from datetime import datetime


class GenerationProcess(BaseModel):
    id: int
    user_id: int
    template_id: int
    created_at: datetime = datetime.now()


class GenerationDocument(BaseModel):
    id: int
    gen_process_id: int
    file_path: str
    created_at: datetime = datetime.now()
