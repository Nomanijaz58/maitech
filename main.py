from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import configurations
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.db.documents.user import User
from app.api.routes.auth import router as auth_router
from fastapi import APIRouter


async def init_db():
    client = AsyncIOMotorClient(configurations.MONGODB_URL)
    db = client.get_default_database()
    await init_beanie(database=db, document_models=[User])


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("Starting up")
    yield
    print("Shutting down")


app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    title="MaiTech API",
    version="1.0.0",
    description="Backend API for MaiTech platform with Cognito-based authentication and MongoDB (Beanie).",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[item.strip() for item in configurations.CORS_ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api")
async def root():
    return {"message": "Welcome to GiF (Growing is Fun) API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
