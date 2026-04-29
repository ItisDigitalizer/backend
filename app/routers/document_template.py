from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import List, Any

from app.dependencies import DocumentTemplateServiceDep
from app.models.document_template import (
    DocumentTemplateCreate,
    DocumentTemplateUpdate,
    DocumentTemplateRead,
)

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post(
    "/", response_model=DocumentTemplateRead, status_code=status.HTTP_201_CREATED
)
async def create_template(
    data: DocumentTemplateCreate, service: DocumentTemplateServiceDep
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
    skip: int = 0,
    limit: int = 100,
    user_id: UUID | None = None,
    name: str | None = None,
) -> Any:
    """Получение списка шаблонов с фильтрацией"""
    if user_id:
        templates = await service.get_by_user_id(user_id)
        return templates[skip : skip + limit]
    if name:
        template = await service.get_by_name(name)
        return [template] if template else []

    return await service.get_all(skip, limit)


@router.get("/{template_id}", response_model=DocumentTemplateRead)
async def get_template(template_id: UUID, service: DocumentTemplateServiceDep) -> Any:
    """Получение шаблона по ID"""
    template = await service.get(template_id)  # type: ignore
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
):
    """Обновление шаблона"""
    template = await service.update_template(template_id, updates)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: UUID, service: DocumentTemplateServiceDep):
    """Удаление шаблона"""
    template = await service.delete_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return None
