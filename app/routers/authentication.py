from fastapi import APIRouter, Depends, HTTPException
from fastapi import Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request

from app.models.user import User, UserCreate, UserRead
from app.auth.utils import get_current_user
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(),
):
    tokens = await service.login(
        form_data.username,
        form_data.password,
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
    )

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserRead)
async def me(
    current_user: User = Depends(get_current_user)
):
    return UserRead.model_validate(current_user)


@router.post("/register")
async def register(
    data: UserCreate,
    service: AuthService = Depends(),
):
    return await service.register(UserCreate(username=data.username, email=data.email, password=data.password)
    )

@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    service: AuthService = Depends(),
):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    tokens = await service.refresh_tokens(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        samesite="lax",
    )

    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(),
):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    await service.logout(refresh_token)

    response.delete_cookie("refresh_token")

    return {"success": True}