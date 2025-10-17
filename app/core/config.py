from decouple import config
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = config("APP_NAME", default="MaiTech")
    FRONTEND_URL: str = config("FRONTEND_URL", default="http://localhost:3000")
    MONGODB_URL: str = config("MONGODB_URL")

    CORS_ALLOWED_ORIGINS: str = config('CORS_ALLOWED_ORIGINS')

    MAIL_FROM: str = config("MAIL_FROM")
    SENDGRID_API_KEY: str = config("SENDGRID_API_KEY")

    # ADMIN_EMAIL: str = config("ADMIN_EMAIL")

    COGNITO_REGION: str = config("COGNITO_REGION")
    COGNITO_USER_POOL_ID: str = config("COGNITO_USER_POOL_ID")
    COGNITO_CLIENT_ID: str = config("COGNITO_CLIENT_ID")

    # S3_REGION: str = config("S3_REGION")
    # S3_ACCESS_KEY_ID: str = config("S3_ACCESS_KEY_ID")
    # S3_SECRET_ACCESS_KEY: str = config("S3_SECRET_ACCESS_KEY")
    # S3_BUCKET_NAME: str = config("S3_BUCKET_NAME")

    class Config:
        extra = "ignore"


configurations = Settings()
