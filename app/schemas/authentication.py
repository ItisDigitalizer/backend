from pydantic import BaseModel
from sqlmodel import SQLModel

from app.models.user import UserRole


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class UserFilters(SQLModel):
    username: str | None = None
    email: str | None = None
    role: UserRole | None = None

    class Config:
        from_attributes = True


class TokenPayload(BaseModel):
    sub: str
    type: str  # "access" / "refresh"
    iat: int
    exp: int
    jti: str