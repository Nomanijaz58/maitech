from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import configurations
from app.db.database import db_service
from app.api.routes.auth import router as auth_router
from fastapi import APIRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB using pymongo
    await db_service.connect()
    print("Starting up")
    yield
    # Disconnect from MongoDB
    await db_service.disconnect()
    print("Shutting down")


app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    title="MaiTech API",
    version="1.0.0",
    description="Backend API for MaiTech platform with Cognito-based authentication and MongoDB.",
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
    return {"message": "Welcome to MaiTech API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
