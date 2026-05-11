from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from app.auth.utils import get_current_user, require_admin
from app.dependencies import GenerationProcessServiceDep, GenerationProcessFiltersDep
from app.models import User, UserRole
from app.models.generation_process import (
    GenerationProcessCreate,
    GenerationProcessRead,
    GenerationProcessUpdate,
)
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
    filters: GenerationProcessFiltersDep,
    service: GenerationProcessServiceDep,
    pagination: PaginationParam = Depends(),
    current_user: User = Depends(get_current_user),
):
    # Пользователь не может просматривать чужие процессы
    if current_user.role == UserRole.USER:
        # Если id не совпадают, значит обычный пользователь хочет просмотреть чужие процессы
        if filters.user_id and filters.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        #Если user_id вообще не передан, то запрещаем просмотр
        elif not filters.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User ID is missing",
            )
    # Если же есть роль менеджера, то ничего дополнительно не делаем,
    # потому что он может смотреть любые процессы

    return await service.get_filtered_process(
        filters,
        pagination.offset,
        pagination.limit,
    )


@router.get("/{process_id}", response_model=GenerationProcessRead)
async def get_process(
    process_id: UUID,
    service: GenerationProcessServiceDep,
    current_user: User = Depends(get_current_user),
):
    """Получение процесса по ID с проверкой прав"""
    process = await service.get(process_id)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Process not found"
        )

    # Проверка, не пытается ли человек без админки посмотреть не свой процесс
    if current_user.role != UserRole.MANAGER and process.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this process",
        )

    return process


@router.patch(
    "/{process_id}",
    response_model=GenerationProcessRead,
    dependencies=[Depends(require_admin)]
)
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


@router.delete(
    "/{process_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)]
)
async def delete_process(
        process_id: UUID,
        service: GenerationProcessServiceDep,
):
    """Удаление процесса"""
    process = await service.delete_process(process_id)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Process not found"
        )
    return None
