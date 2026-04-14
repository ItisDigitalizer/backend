from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.auth.utils import SECRET_KEY, ALGORITHM
from app.repositories.user import UserRepo

from app.auth.service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepo = Depends()
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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


def get_user_repository():
    return UserRepo()


def get_auth_service(
    user_repo: UserRepo = Depends(get_user_repository),
):
    return AuthService(user_repo=user_repo)