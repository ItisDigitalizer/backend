from fastapi import FastAPI

app = FastAPI(
    title="Digitalizer",
    description="Service for document generation from templates",
    version="0.1.0",
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.get("/")
async def root():
    return {"message": "Digitalizer API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
