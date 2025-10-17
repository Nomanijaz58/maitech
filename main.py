from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.db import init_db


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
    title="GiF (Growing is Fun) API",
    version="1.0.0",
    description="API for GiF (Growing is Fun)",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api", dependencies=[Depends(get_current_user)])
async def root():
    return {"message": "Welcome to GiF (Growing is Fun) API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
