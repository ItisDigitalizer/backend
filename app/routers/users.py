# app/api/v1/endpoints/users.py
from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import List, Any

from app.models import UserRole
from app.dependencies import UserServiceDep
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserFilters

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, service: UserServiceDep):
    """Создание нового пользователя"""
    try:
        user = await service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[UserResponse])
async def get_users(
    service: UserServiceDep,
    skip: int = 0,
    limit: int = 100,
    username: str | None = None,
    email: str | None = None,
    role: UserRole | None = UserRole.USER,
) -> Any:
    """Получение списка пользователей с фильтрацией"""
    filters = UserFilters(username=username, email=email, role=role)
    users = await service.get_filtered_users(filters, skip, limit)
    return users


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    # Здесь будет current_user после реализации аутентификации
    service: UserServiceDep,
):
    """Получение текущего пользователя (заглушка)"""
    # TODO: реализовать получение текущего пользователя из токена
    pass


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, service: UserServiceDep) -> Any:
    """Получение пользователя по ID"""
    user = await service.get(user_id)  # type: ignore
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
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
