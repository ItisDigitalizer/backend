# app/api/v1/endpoints/users.py
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from app.dependencies import UserServiceDep
from app.models.user import UserCreate, UserRead, UserUpdate
from app.schemas.pagination import PaginationParam
from app.schemas.user import UserFilters

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, service: UserServiceDep):
    """Создание нового пользователя"""
    try:
        user = await service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[UserRead])
async def get_users(
    service: UserServiceDep,
    pagination: PaginationParam = Depends(),
    filters: UserFilters = Depends(),
):
    """Получение списка пользователей с фильтрацией"""
    users = await service.get_filtered_users(filters, pagination.skip, pagination.limit)
    return users


@router.get("/me", response_model=UserRead)
async def get_current_user(
    # Здесь будет current_user после реализации аутентификации
    service: UserServiceDep,
):
    """Получение текущего пользователя (заглушка)"""
    # TODO: реализовать получение текущего пользователя из токена
    pass


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, service: UserServiceDep):
    """Получение пользователя по ID"""
    user = await service.get(user_id)  # type: ignore
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: UUID, updates: UserUpdate, service: UserServiceDep):
    """Обновление пользователя"""
    try:
        user = await service.update_user(user_id, updates)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, service: UserServiceDep):
    """Удаление пользователя"""
    user = await service.delete_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return None
