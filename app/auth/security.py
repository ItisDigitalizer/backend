#app/auth/security.py
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core.settings import settings
from app.schemas.authentication import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)

    payload = TokenPayload(
        sub=subject,
        type="access",
        iat=int(now.timestamp()),
        exp=int(
            (now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp()
        ),
        jti=str(uuid4()),
    )

    return jwt.encode(
        payload.model_dump(),
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_refresh_token(subject: str) -> tuple[str, TokenPayload]:
    now = datetime.now(timezone.utc)

    payload = TokenPayload(
        sub=subject,
        type="refresh",
        iat=int(now.timestamp()),
        exp=int(
            (
                now + timedelta(days=settings.refresh_token_expire_days)
            ).timestamp()
        ),
        jti=str(uuid4()),
    )

    token = jwt.encode(
        payload.model_dump(),
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    return token, payload


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except JWTError:
        raise ValueError("Invalid token")


def decode_access_token(token: str) -> dict:
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise ValueError("Invalid token type")

    return payload


def decode_refresh_token(token: str) -> dict:
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type")

    return payload