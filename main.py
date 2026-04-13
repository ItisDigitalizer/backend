from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel

from app.exceptions import NotFoundError
from app.models import User
from app.repositories.user import UserRepo
from app.schemas.users import CreateUserRequest
from app.services.user import UserService
from dependencies import ServiceDep, engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("App started")
    SQLModel.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False, class_=Session)
    repo = UserRepo(session_factory=factory)
    app.state.service = UserService(repo)
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
