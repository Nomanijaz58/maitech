from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import configurations
from app.api.routes.auth import router as auth_router
from app.api.routes.user_routes import router as user_router
from app.api.routes.student_api import router as student_router
from app.api.routes.reports import router as reports_router
from app.api.routes.class_chat import router as class_chat_router
from app.api.routes.settings import router as settings_router
from app.api.routes.teacher import teacher_router
from app.api.v1.routes.notifications import router as notifications_router
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Beanie ODM with AsyncMongoClient
    try:
        await init_db()
        print("✅ Beanie ODM initialized successfully")
    except Exception as e:
        print(f"❌ Beanie init failed: {e}")
        raise
    print("🚀 Starting up MaiTech API")
    yield
    print("🛑 Shutting down")


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
# Forgot/Reset password routes removed per requirements
app.include_router(student_router)
app.include_router(reports_router)
app.include_router(class_chat_router)
app.include_router(settings_router)
app.include_router(teacher_router)
app.include_router(notifications_router)

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/ping-db")
async def ping_db():
    """
    Test database connection using Beanie.
    Returns user count to verify connection is working.
    """
    from app.db.documents.user import User
    try:
        count = await User.find_all().count()
        return {"status": "connected", "users_in_db": count, "message": "Database connection successful"}
    except Exception as e:
        return {"status": "error", "message": f"Database connection failed: {str(e)}"}


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
                "confirm": "/api/auth/confirm"
            },
            "users": {
                "create": "/api/users/",
                "get_all": "/api/users/",
                "get_by_id": "/api/users/{user_id}"
            },
            "student": {
                "dashboard": "/api/student/dashboard",
                "learning_path": "/api/student/learning-path",
                "lessons": "/api/student/lessons",
                "lesson_history": "/api/student/lessons/history",
                "lesson_details": "/api/student/lessons/{lesson_id}"
            }
        }
    }

@app.get("/api")
async def api_root():
    return {"message": "Welcome to MaiTech API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
