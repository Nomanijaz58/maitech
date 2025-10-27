from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import configurations
from app.db.database import db_service
from app.api.routes.auth import router as auth_router
from app.api.routes.user_routes import router as user_router
from fastapi import APIRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB using pymongo (synchronous operation)
    db_service.connect()
    print("Starting up")
    yield
    # Disconnect from MongoDB (synchronous operation)
    db_service.disconnect()
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
app.include_router(user_router)

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root_redirect():
    return {
        "message": "Welcome to MaiTech API",
        "docs": "Visit /api/docs for API documentation",
        "health": "Visit /api/health for health check",
        "endpoints": {
            "health": "/api/health",
            "docs": "/api/docs",
            "auth": {
                "register": "/api/auth/register",
                "confirm": "/api/auth/confirm", 
                "login": "/api/auth/login"
            },
            "users": {
                "create": "/api/users/",
                "get_all": "/api/users/",
                "get_by_id": "/api/users/{user_id}"
            }
        }
    }

@app.get("/api")
async def api_root():
    return {"message": "Welcome to MaiTech API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
