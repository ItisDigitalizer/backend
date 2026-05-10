from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from app.auth.utils import get_current_user, require_admin
from app.dependencies import GenerationProcessServiceDep
from app.models import User, UserRole
from app.models.generation_process import (
    GenerationProcessCreate,
    GenerationProcessRead,
    GenerationProcessUpdate,
)
from app.schemas.generation_process import GenerationProcessFilters
from app.schemas.pagination import PaginationParam

router = APIRouter(prefix="/processes", tags=["processes"])


@router.post(
    "/", response_model=GenerationProcessRead, status_code=status.HTTP_201_CREATED
)
async def create_process(
    data: GenerationProcessCreate, service: GenerationProcessServiceDep
):
    """Создание нового процесса генерации"""
    try:
        process = await service.create_process(data)
        return process
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[GenerationProcessRead])
async def get_processes(
    service: GenerationProcessServiceDep,
    pagination: PaginationParam = Depends(),
    current_user: User = Depends(get_current_user),
    user_id: UUID | None = None,
    template_id: UUID | None = None,
):
    # Для обычного пользователя только его процессы
    if current_user.role != UserRole.MANAGER:
        user_id = current_user.id

    filters = GenerationProcessFilters(
        user_id=user_id,
        template_id=template_id,
    )

    return await service.get_filtered_process(
        filters,
        pagination.offset,
        pagination.limit,
    )


@router.get("/{process_id}", response_model=GenerationProcessRead)
async def get_process(process_id: UUID, service: GenerationProcessServiceDep):
    """Получение процесса по ID"""
    process = await service.get(process_id)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Process not found"
        )
    return process


@router.patch("/{process_id}", response_model=GenerationProcessRead)
async def update_process(
    process_id: UUID,
    updates: GenerationProcessUpdate,
    service: GenerationProcessServiceDep,
):
    """Обновление процесса"""
    process = await service.update_process(process_id, updates)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Process not found"
        )
    return process


@router.delete("/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_process(
        process_id: UUID,
        service: GenerationProcessServiceDep,
        current_user: User = Depends(require_admin),
):
    """Удаление процесса"""
    process = await service.delete_process(process_id)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Process not found"
        )
    return None
