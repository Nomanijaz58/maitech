from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import configurations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await init_db()
    print("Starting up")
    yield
    print("Shutting down")


app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    title="MaiTech API",
    version="1.0.0",
    description="API for MaiTech",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[item.strip() for item in configurations.CORS_ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api")
async def root():
    return {"message": "Welcome to GiF (Growing is Fun) API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
