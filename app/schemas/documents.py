from pydantic import BaseModel


class CreateGenerationProcessRequest(BaseModel):
    user_id: int
    template_id: int


class UpdateGenerationProcessRequest(BaseModel):
    user_id: int | None = None
    template_id: int | None = None


class CreateGeneratedDocumentRequest(BaseModel):
    gen_process_id: int
    file_path: str


class UpdateGeneratedDocumentRequest(BaseModel):
    gen_process_id: int | None = None
    file_path: str | None = None
