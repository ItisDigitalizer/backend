from typing import List
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.params import Depends

from app.auth.utils import require_admin
from app.dependencies import DocumentGeneratorServiceDep, DocumentTemplateServiceDep
from app.models.document_template import (
    DocumentTemplateRead,
    DocumentTemplateUpdate,
)
from app.schemas.document_template import DocumentTemplateFilters
from app.schemas.pagination import PaginationParam

router = APIRouter(prefix="/templates", tags=["templates"])


# @router.post(
#     "/",
#     response_model=DocumentTemplateRead,
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(require_admin)],
# )
# async def create_template(
#     data: DocumentTemplateCreate,
#     service: DocumentTemplateServiceDep,
# ):
#     """Создание нового шаблона"""
#     try:
#         return await service.create_template(data)
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e),
#         )


@router.post("/", response_model=DocumentTemplateRead, status_code=201)
async def create_template(
    *,
    name: str = Form(...),
    description: str = Form(None),
    docx_file: UploadFile = File(...),
    current_user=Depends(require_admin),
    service: DocumentTemplateServiceDep,
):
    """Создание шаблона + загрузка DOCX"""

    if not docx_file.filename.lower().endswith(".docx"):
        raise HTTPException(400, "Только DOCX")

    content = await docx_file.read()

    template = await service.create_template_with_file(
        name=name,
        description=description,
        docx_content=content,
        user_id=current_user.id,
    )

    return template


@router.get("/", response_model=List[DocumentTemplateRead])
async def get_templates(
    service: DocumentTemplateServiceDep,
    pagination: PaginationParam = Depends(),
    user_id: UUID | None = None,
    name: str | None = None,
):
    """Получение списка шаблонов с фильтрацией"""
    filters = DocumentTemplateFilters(user_id=user_id, name=name)
    return await service.get_filtered_templates(
        filters, pagination.offset, pagination.limit
    )


@router.get("/{template_id}", response_model=DocumentTemplateRead)
async def get_template(template_id: UUID, service: DocumentTemplateServiceDep):
    """Получение шаблона по ID"""
    template = await service.get(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return template


@router.get("/pdf/{template_id}")
async def get_pdf_template(
    template_id: UUID,
    template_service: DocumentTemplateServiceDep,
    gen_service: DocumentGeneratorServiceDep,
):
    template = await template_service.get(template_id)
    if not template:
        raise HTTPException(404, "Template not found")

    if not template.file_path:
        raise HTTPException(400, "Template file path is missing")

    pdf_path = gen_service.convert_to_pdf_sync(template.file_path)

    return {"pdf_path": pdf_path}


@router.patch(
    "/{template_id}",
    response_model=DocumentTemplateRead,
    dependencies=[Depends(require_admin)],
)
async def update_template(
    template_id: UUID,
    updates: DocumentTemplateUpdate,
    service: DocumentTemplateServiceDep,
):
    """Обновление шаблона"""
    template = await service.update_template(template_id, updates)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return template


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_template(
    template_id: UUID,
    service: DocumentTemplateServiceDep,
):
    """Удаление шаблона"""
    template = await service.delete_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return None
