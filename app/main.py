from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger

from app.routers import (
    users,
    generated_document,
    generation_process,
    document_template,
    template_field,
    authentication
)
from fastapi import APIRouter


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

# router.include_router(templates.router)
# router.include_router(documents.router)

api_router.include_router(generated_document.router)
api_router.include_router(generation_process.router)
api_router.include_router(document_template.router)
api_router.include_router(template_field.router)
app.include_router(api_router)
