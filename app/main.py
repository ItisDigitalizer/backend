from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from loguru import logger

from app.routers import (
    authentication,
    document_template,
    generated_document,
    generation,
    generation_process,
    health,
    template_field,
    users,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App started")
    yield
    logger.info("App stopped")


app = FastAPI(
    title="Digitalizer",
    description="Service for document generation from templates",
    version="0.1.0",
    lifespan=lifespan,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(users.router)
api_router.include_router(authentication.router)
api_router.include_router(generated_document.router)
api_router.include_router(generation_process.router)
api_router.include_router(document_template.router)
api_router.include_router(template_field.router)
api_router.include_router(generation.router)
app.include_router(health.router)
app.include_router(api_router)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",
#         "http://95.174.93.115",
#         "http://95.174.93.115:5173",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
