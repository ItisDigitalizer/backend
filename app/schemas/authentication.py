from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class TokenPayload(BaseModel):
    sub: str
    type: str  # "access" / "refresh"
    iat: int
    exp: int
    jti: UUID


class RefreshSessionFilters(BaseModel):
    jti: UUID | None = None
    user_id: UUID | None = None


class LogoutResponse(BaseModel):
    success: bool
    message: str | None = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
