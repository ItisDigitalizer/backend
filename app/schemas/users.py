from pydantic import BaseModel, EmailStr
from app.models import UserRole


class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password_hash: str
    role: UserRole = UserRole.USER
