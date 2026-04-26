from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlmodel import select

from app.schemas.authentication import *
from app.auth.utils import *
from app.models.user import User
from app.db.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    return service.login(data)


@router.get("/me")
def me(user=Depends(get_current_user)):
    return user


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    statement = select(User).where(User.username == user.username)
    existing_user = db.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    statement = select(User).where(User.email == user.email)
    existing_email = db.exec(statement).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }