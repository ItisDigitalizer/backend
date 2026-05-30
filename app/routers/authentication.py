from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.params import Cookie
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.utils import get_current_user
from app.dependencies import AuthServiceDep
from app.models.user import User, UserCreate, UserRead
from app.schemas.authentication import LogoutResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
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

    return tokens


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return UserRead.model_validate(current_user)


@router.post("/register")
async def register(
    data: UserCreate,
    service: AuthServiceDep,
):
    return await service.register(data)


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
