from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.user import User
from app.schemas.authentication import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    ChangePasswordRequest,
)
from app.auth.utils import get_current_user, get_auth_service
from app.services.auth_service import AuthService
from app.auth.security import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(
        form_data.username,
        form_data.password,
    )


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return user


@router.post("/register")
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    # check username
    result = await db.execute(
        select(User).where(User.username == user.username)
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # check email
    result = await db.execute(
        select(User).where(User.email == user.email)
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role,
    }


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.change_password(
        user_id=current_user.id,
        old_password=data.old_password,
        new_password=data.new_password,
    )

    return {"status": "ok"}