from pydantic import BaseModel


class CreateDocumentTemplateRequest(BaseModel):
    name: str
    description: str
    user_id: int
    file_path: int


class UpdateDocumentTemplateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    user_id: int | None = None
    file_path: int | None = None


class CreateTemplateFieldRequest(BaseModel):
    template_id: int
    name: str
    description: str


class UpdateTemplateFieldRequest(BaseModel):
    template_id: int | None = None
    name: str | None = None
    description: str | None = None
