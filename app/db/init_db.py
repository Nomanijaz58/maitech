from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import configurations
from app.db.documents.user import User
from app.db.documents.notification import Notification

DATABASE_MODELS = [User, Notification]


async def init_db():
    client = AsyncIOMotorClient(configurations.MONGODB_URL)
    await init_beanie(
        database=client.get_default_database(),
        document_models=DATABASE_MODELS,
    )
    for model in DATABASE_MODELS:
        try:
            model.model_rebuild()
        except Exception:
            pass

