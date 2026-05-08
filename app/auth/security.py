from passlib.context import CryptContext
from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = Settings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise ValueError("Invalid token")


def decode_refresh_token(token: str) -> dict:
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type")

    return payload


def decode_access_token(token: str) -> dict:
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise ValueError("Invalid token type")

    return payload