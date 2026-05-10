from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from app.auth.utils import require_admin
from app.dependencies import DocumentTemplateServiceDep
from app.models import User
from app.models.document_template import (
    DocumentTemplateCreate,
    DocumentTemplateRead,
    DocumentTemplateUpdate,
)
from app.schemas.document_template import DocumentTemplateFilters
from app.schemas.pagination import PaginationParam

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post(
    "/", response_model=DocumentTemplateRead, status_code=status.HTTP_201_CREATED
)
async def create_template(
    data: DocumentTemplateCreate, service: DocumentTemplateServiceDep,
    current_user: User = Depends(require_admin),
):
    """Создание нового шаблона"""
    try:
        template = await service.create_template(data)
        return template
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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


@router.patch("/{template_id}", response_model=DocumentTemplateRead)
async def update_template(
    template_id: UUID,
    updates: DocumentTemplateUpdate,
    service: DocumentTemplateServiceDep,
    current_user: User = Depends(require_admin),
):
    """Обновление шаблона"""
    template = await service.update_template(template_id, updates)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
        template_id: UUID,
        service: DocumentTemplateServiceDep,
        current_user: User = Depends(require_admin),
):
    """Удаление шаблона"""
    template = await service.delete_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return None
