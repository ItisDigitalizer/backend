from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
from db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App started")
    await init_db()
    yield
    logger.info("App stopped")


app = FastAPI(
    title="Digitalizer",
    description="Service for document generation from templates",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
