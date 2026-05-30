from sqlmodel import SQLModel


class PdfResponse(SQLModel):
    pdf_path: str
