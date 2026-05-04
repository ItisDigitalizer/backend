from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from app.dependencies import TemplateFieldServiceDep
from app.models.template_field import (
    TemplateFieldCreate,
    TemplateFieldRead,
    TemplateFieldUpdate,
)
from app.schemas.pagination import PaginationParam
from app.schemas.template_field import TemplateFieldFilters

router = APIRouter(prefix="/fields", tags=["fields"])


@router.post("/", response_model=TemplateFieldRead, status_code=status.HTTP_201_CREATED)
async def create_field(data: TemplateFieldCreate, service: TemplateFieldServiceDep):
    """Создание нового поля шаблона"""
    try:
        field = await service.create_field(data)
        return field
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[TemplateFieldRead])
async def get_fields(
    service: TemplateFieldServiceDep,
    pagination: PaginationParam = Depends(),
    template_id: UUID | None = None,
):
    """Получение списка полей с фильтрацией по шаблону"""
    filters = TemplateFieldFilters(template_id=template_id)
    return await service.get_filtered_field(filters, pagination.skip, pagination.limit)


@router.get("/{field_id}", response_model=TemplateFieldRead)
async def get_field(field_id: UUID, service: TemplateFieldServiceDep):
    """Получение поля по ID"""
    field = await service.get(field_id)  # type: ignore
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Field not found"
        )
    return field


@router.patch("/{field_id}", response_model=TemplateFieldRead)
async def update_field(
    field_id: UUID,
    updates: TemplateFieldUpdate,
    service: TemplateFieldServiceDep,
):
    """Обновление поля"""
    field = await service.update_field(field_id, updates)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Field not found"
        )
    return field


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field(field_id: UUID, service: TemplateFieldServiceDep):
    """Удаление поля"""
    field = await service.delete_field(field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Field not found"
        )
    return None
