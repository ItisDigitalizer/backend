from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.params import Cookie
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.utils import get_current_user
from app.dependencies import AuthServiceDep
from app.models.user import User, UserCreate, UserRead
from app.schemas.authentication import (
    ActionSuccessResponse,
    ChangePasswordRequest,
    EmailNotificationResponse,
    ForgotPasswordRequest,
    LogoutResponse,
    ResetPasswordRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserRead)
async def login(
    response: Response,
    service: AuthServiceDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    tokens = await service.login(
        form_data.username,
        form_data.password,
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
    )

    return tokens.user


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return UserRead.model_validate(current_user)


@router.post("/register", response_model=EmailNotificationResponse)
async def register(
    data: UserCreate,
    service: AuthServiceDep,
    background_tasks: BackgroundTasks,
    request: Request,
):
    return await service.register(data, background_tasks, request)


@router.get("/verify-account", response_model=ActionSuccessResponse)
async def verify_account(
    token: str,
    service: AuthServiceDep,
):
    return await service.verify_account(token)


@router.post("/forgot-password", response_model=EmailNotificationResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    service: AuthServiceDep,
    background_tasks: BackgroundTasks,
):
    return await service.forgot_password(data, background_tasks)


@router.post("/reset-password", response_model=ActionSuccessResponse)
async def reset_password(
    data: ResetPasswordRequest,
    service: AuthServiceDep,
):
    return await service.reset_password(data)


@router.post("/change-password", response_model=ActionSuccessResponse)
async def change_password(
    data: ChangePasswordRequest,
    service: AuthServiceDep,
    current_user: User = Depends(get_current_user),
):
    return await service.change_password(current_user, data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    service: AuthServiceDep,
    refresh_token: str | None = Cookie(default=None),
):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    tokens = await service.refresh_tokens(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
    )

    return tokens


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    service: AuthServiceDep,
    response: Response,
    refresh_token: str | None = Cookie(default=None),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        await service.logout(refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    response.delete_cookie("refresh_token")

    return LogoutResponse(success=True)
