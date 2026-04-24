from fastapi import FastAPI

app = FastAPI(
    title="Digitalizer",
    description="Service for document generation from templates",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
