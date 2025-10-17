from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.core.config import settings
from app.db.documents.user import User

DATABASE_MODELS = [User]


async def init_db():
    """
    Initializes the database connection and sets up Beanie ODM.

    This function connects to the MongoDB instance via the MongoDB URL specified
    in the settings and initializes Beanie with the provided database models. It
    is intended to be used in an asynchronous context. This setup is essential for
    working with the defined database models using Beanie.

    :return: None
    """

    client = AsyncMongoClient(settings.MONGODB_URL)
    await init_beanie(
        database=client.db_name,
        document_models=DATABASE_MODELS,
    )

    for model in DATABASE_MODELS:
        try:
            model.model_rebuild()
        except Exception:
            pass
