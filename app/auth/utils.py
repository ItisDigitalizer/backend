#app/auth/utils.py
from uuid import UUID

from fastapi import Depends, HTTPException, status
from jose import JWTError

from app.auth.security import (
    oauth2_scheme,
    decode_access_token,
)
from app.models import User, UserRole
from app.repositories.user_repo import UserRepository


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(),
):
    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

        user = await user_repo.get(UUID(user_id))

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found",
            )

        return user

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only",
        )
    return current_user