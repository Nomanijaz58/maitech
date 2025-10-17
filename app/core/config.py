from decouple import config
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = config("APP_NAME", default="Dialex AI")
    FRONTEND_URL: str = config("FRONTEND_URL", default="http://localhost:3000")
    MONGODB_URL: str = config("MONGODB_URL")

    CORS_ALLOWED_ORIGINS: list[str] = config("CORS_ALLOWED_ORIGINS", cast=list)

    MAIL_USERNAME: str = config("MAIL_USERNAME")
    MAIL_PASSWORD: str = config("MAIL_PASSWORD")
    MAIL_PORT: int = config("MAIL_PORT", cast=int)
    MAIL_SERVER: str = config("MAIL_SERVER")
    MAIL_STARTTLS: bool = config("MAIL_STARTTLS", cast=bool)
    MAIL_SSL_TLS: bool = config("MAIL_SSL_TLS", cast=bool)

    MAIL_FROM: str = config("MAIL_FROM")
    MAIL_FROM_NAME: str = config("MAIL_FROM_NAME")

    COGNITO_REGION: str = config("COGNITO_REGION")
    COGNITO_USER_POOL_ID: str = config("COGNITO_USER_POOL_ID")
    COGNITO_CLIENT_ID: str = config("COGNITO_CLIENT_ID")

    class Config:
        extra = "ignore"


settings = Settings()
