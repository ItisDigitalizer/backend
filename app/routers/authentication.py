from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.dependencies import AuthServiceDep
from app.models.user import User
from app.schemas.authentication import (
    LoginRequest,
    TokenResponse,
    UserCreate,
)
from app.auth.utils import get_current_user, get_auth_service
from app.services.auth_service import AuthService
from app.auth.security import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(
        username=form_data.username,
        password=form_data.password,
    )


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return user


@router.post("/register")
async def register(
    data: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    return await service.register(
        username=data.username,
        email=data.email,
        password=data.password,
    )
