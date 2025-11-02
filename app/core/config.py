from decouple import config
from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = config("APP_NAME", default="MaiTech")
    FRONTEND_URL: str = config("FRONTEND_URL", default="http://localhost:3000")
    MONGODB_URL: str = config("MONGODB_URL")

    CORS_ALLOWED_ORIGINS: str = config('CORS_ALLOWED_ORIGINS')

    MAIL_FROM: str = config("MAIL_FROM")
    SENDGRID_API_KEY: str = config("SENDGRID_API_KEY")

    # ADMIN_EMAIL: str = config("ADMIN_EMAIL")

    # AWS credentials (optional locally if using IAM role)
    AWS_REGION: str = config("AWS_REGION", default="")
    AWS_ACCESS_KEY_ID: str = config("AWS_ACCESS_KEY_ID", default="")
    AWS_SECRET_ACCESS_KEY: str = config("AWS_SECRET_ACCESS_KEY", default="")
    # Cognito required settings
    COGNITO_REGION: str = config("COGNITO_REGION")
    COGNITO_USER_POOL_ID: str = config("COGNITO_USER_POOL_ID")
    COGNITO_CLIENT_ID: str = config("COGNITO_CLIENT_ID")

    # S3_REGION: str = config("S3_REGION")
    # S3_ACCESS_KEY_ID: str = config("S3_ACCESS_KEY_ID")
    # S3_SECRET_ACCESS_KEY: str = config("S3_SECRET_ACCESS_KEY")
    # S3_BUCKET_NAME: str = config("S3_BUCKET_NAME")

    class Config:
        extra = "ignore"

    def validate_required(self) -> None:
        missing = []
        if not self.MONGODB_URL:
            missing.append("MONGODB_URL")
        if not self.COGNITO_REGION:
            missing.append("COGNITO_REGION")
        if not self.COGNITO_USER_POOL_ID:
            missing.append("COGNITO_USER_POOL_ID")
        if not self.COGNITO_CLIENT_ID:
            missing.append("COGNITO_CLIENT_ID")
        # Access keys are optional if using IAM role/environment provider
        if missing:
            keys = ", ".join(missing)
            raise RuntimeError(f"Missing required environment variables: {keys}")


configurations = Settings()
configurations.validate_required()
