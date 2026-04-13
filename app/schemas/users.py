from pydantic import BaseModel, EmailStr
from app.models import UserRole


class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password_hash: str
    role: UserRole = UserRole.USER


class UpdateUserRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password_hash: str | None = None
    role: UserRole | None = None
