# app/api/v1/endpoints/users.py
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.sql.functions import current_user

from app.auth.utils import get_current_user
from app.dependencies import UserServiceDep
from app.models.user import UserCreate, UserRead, UserRole, UserUpdate, User
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
    username: str | None = None,
    email: str | None = None,
    role: UserRole | None = UserRole.USER,
) -> Any:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "Not enough permissions")
    """Получение списка пользователей с фильтрацией"""
    filters = UserFilters(username=username, email=email, role=role)
    users = await service.get_filtered_users(filters, pagination.skip, pagination.limit)
    return users


@router.get("/me", response_model=UserRead)
async def get_current_user_route(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, service: UserServiceDep) -> Any:
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
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "Forbidden")
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
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "Forbidden")
    user = await service.delete_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return None
