from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from loguru import logger

from app.auth.utils import get_current_user
from app.dependencies import (
    DocumentGeneratorServiceDep,
    DocumentTemplateServiceDep,
    GeneratedDocumentServiceDep,
    GenerationProcessServiceDep,
)
from app.models import User
from app.models.generated_document import GeneratedDocumentCreate
from app.models.generation_process import GenerationProcessCreate

router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("/from-excel/", status_code=201)
async def generate_from_excel(
    template_service: DocumentTemplateServiceDep,
    generator: DocumentGeneratorServiceDep,
    process_service: GenerationProcessServiceDep,
    doc_service: GeneratedDocumentServiceDep,
    template_id: UUID = Form(...),
    excel_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Excel → DOCX/ZIP"""

    # 1. Проверяем шаблон
    template = await template_service.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон не найден")

    # 2. Читаем Excel
    if not excel_file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Excel файл")
    content = await excel_file.read()
    data_list = generator.excel_to_dicts(content)
    if not data_list:
        raise HTTPException(400, "Excel пуст")

    # 3. Создаём процесс
    process = await process_service.create_process(
        GenerationProcessCreate(user_id=current_user.id, template_id=template_id)
    )

    # 4. Генерируем
    result_path = await generator.generate_documents(
        template.file_path,  # ← из БД!
        data_list,
        str(process.id),
    )

    # 5. Сохраняем документ
    doc = await doc_service.create_document(
        GeneratedDocumentCreate(gen_process_id=process.id, file_path=result_path)
    )
    logger.info(f"Создали документ {doc.id} для процесса {process.id}")
    return {
        "process_id": str(process.id),
        "download": f"/generate/download/{process.id}/",
        "files": len(data_list),
    }


@router.get("/download/{process_id}/")
async def download_result(process_id: UUID, doc_service: GeneratedDocumentServiceDep):
    docs = await doc_service.get_by_process_id(process_id, 0, 1)
    if not docs:
        raise HTTPException(404, "Процесс не найден")

    doc = docs[0]
    filename = "documents.zip" if ".zip" in doc.file_path else "document.docx"

    return FileResponse(
        path=doc.file_path,
        filename=filename,
        media_type="application/zip"
        if ".zip" in doc.file_path
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
