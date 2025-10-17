from beanie import Document
from pydantic import EmailStr, Field
from datetime import datetime
from typing import Optional

from app.utils.helper import utc_now


class User(Document):
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "users"
