from fastapi import APIRouter, Depends
from app.auth.schemas import LoginRequest, TokenResponse
from app.auth.service import AuthService
from app.auth.dependencies import get_auth_service, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    return service.login(data)


@router.get("/me")
def me(user=Depends(get_current_user)):
    return user