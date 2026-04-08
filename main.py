from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Request
from loguru import logger
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine

from app.exceptions import NotFoundError
from app.models import User
from app.repo import Repo
from app.schemas.users import CreateUserRequest
from app.service import Service
from dependencies import get_service, get_settings
from fastapi.responses import JSONResponse

ServiceDep = Annotated[Service, Depends(get_service)]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("App started")
    engine = create_engine(
        get_settings().DATABASE_URL, connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False, class_=Session)
    repo = Repo(session_factory=factory)
    app.state.service = Service(repo)
    yield
    logger.info("App stopped")


app = FastAPI(
    title="Digitalizer",
    description="Service for document generation from templates",
    version="0.1.0",
    lifespan=lifespan,
)


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content=str(exc))


@app.get("/")
async def root():
    return {"message": "Digitalizer API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


users_router = APIRouter(tags=["User management"])


@users_router.get("/one/{user_id}")
async def user(service: ServiceDep, user_id: int) -> User:
    return service.get_user(user_id)


@users_router.get("/all")
async def users(service: ServiceDep) -> list[User]:
    return service.get_users()


@users_router.post("/create")
async def create_user(service: ServiceDep, create_request: CreateUserRequest) -> User:
    user = User.model_validate(create_request.model_dump())
    logger.info(f"creating user({user})")
    created_user = service.create_user(user)
    logger.success(f"{created_user} created")
    return created_user


app.include_router(users_router, prefix="/user")
