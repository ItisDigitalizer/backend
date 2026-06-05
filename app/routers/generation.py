import io
import zipfile
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from loguru import logger

from app.auth.utils import get_current_user
from app.dependencies import (
    DocumentGeneratorServiceDep,
    DocumentTemplateServiceDep,
    GeneratedDocumentServiceDep,
    GenerationProcessServiceDep,
)
from app.models import User
from app.models.generation_process import GenerationProcessCreate
from app.schemas.generation import GenerateResponse, ManualDataRequest

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
    if not template.file_path:
        raise HTTPException(500, "У шаблона нет файла")

    # 2. Читаем Excel
    if not excel_file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Excel файл")
    content = await excel_file.read()
    data_list = generator.excel_to_dicts(content)
    if not data_list:
        raise HTTPException(400, "Excel пуст")

    # 3. Создаём процесс
    process = await process_service.create_process(GenerationProcessCreate(user_id=current_user.id, template_id=template_id))

    # 4. Генерируем
    result_path = await generator.generate_documents(
        doc_service,
        template.file_path,  # ← из БД!
        data_list,
        str(process.id),
    )

    logger.info(f"Создали документы {result_path} для процесса {process.id}")
    return GenerateResponse(
        process_id=str(process.id),
        download=f"/generate/download/{process.id}/",
        files=len(data_list),
    )


@router.post("/manual/", status_code=201)
async def generate_manual(
    template_service: DocumentTemplateServiceDep,
    generator: DocumentGeneratorServiceDep,
    process_service: GenerationProcessServiceDep,
    doc_service: GeneratedDocumentServiceDep,
    request: ManualDataRequest,
    template_id: UUID = Form(...),
    current_user: User = Depends(get_current_user),
):
    """Ручное заполнение — один документ"""

    # 1. Проверяем шаблон
    template = await template_service.get(template_id)
    if not template or not template.file_path:
        raise HTTPException(404, "Шаблон не найден")

    # 2. Создаём процесс
    process = await process_service.create_process(GenerationProcessCreate(user_id=current_user.id, template_id=template_id))

    # 3. Генерируем документ (один словарь → список из одного)
    data_list = [request.data]
    result_path = await generator.generate_documents(
        doc_service,
        template.file_path,
        data_list,
        str(process.id),
    )
    logger.info(f"Создали документы {result_path} для процесса {process.id}")
    return GenerateResponse(
        process_id=str(process.id),
        download=f"/generate/download/{process.id}/",
        files=1,
    )


@router.get("/download/{process_id}/")
async def download_result(process_id: UUID, doc_service: GeneratedDocumentServiceDep):
    docs = await doc_service.get_by_process_id(process_id, 0, 100)
    if not docs:
        raise HTTPException(404, "Процесс не найден")

    if len(docs) == 1:
        doc = docs[0]
        filename = Path(doc.file_path).name
        return FileResponse(
            path=doc.file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for doc in docs:
            if Path(doc.file_path).exists():
                zipf.write(doc.file_path, Path(doc.file_path).name)

    zip_buffer.seek(0)

    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=documents_{process_id}.zip"},
    )
