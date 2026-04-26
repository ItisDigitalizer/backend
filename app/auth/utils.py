from passlib.context import CryptContext
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

import app.models
from app.core.settings import Settings
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=Settings.access_token_expire_minutes)
    payload.update({"exp": expire})
    return jwt.encode(payload, Settings.secret_key, algorithm=Settings.algorithm)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends()
) -> app.models.User:
    try:
        payload = jwt.decode(token, Settings.secret_key, algorithms=[Settings.algorithm])
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(401, "Invalid token")

        user = user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(401, "User not found")

        return user

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def get_auth_service(
    user_repo: UserRepository = Depends(UserRepository),
) -> app.services.auth_service.AuthService:
    return AuthService(user_repo=user_repo)