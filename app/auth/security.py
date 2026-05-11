#app/auth/security.py
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core.settings import settings
from app.schemas.authentication import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
) -> tuple[str, TokenPayload]:

    now = datetime.now(timezone.utc)

    payload = TokenPayload(
        sub=subject,
        type=token_type,
        iat=int(now.timestamp()),
        exp=int((now + expires_delta).timestamp()),
        jti=uuid4(),
    )

    token = jwt.encode(
        payload.model_dump(mode="json"),
        settings.auth.secret_key,
        algorithm=settings.auth.algorithm,
    )

    return token, payload


def create_access_token(subject: str) -> str:
    token, _ = _create_token(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(
            minutes=settings.auth.access_token_expire_minutes
        ),
    )

    return token


def create_refresh_token(subject: str) -> tuple[str, TokenPayload]:
    return _create_token(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(
            days=settings.auth.refresh_token_expire_days
        ),
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.auth.secret_key,
            algorithms=[settings.auth.algorithm],
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