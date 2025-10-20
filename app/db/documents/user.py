from beanie import Document
from pydantic import EmailStr, Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


def utc_now():
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    customer = "customer"
    seller = "seller"
    admin = "admin"


class User(Document):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.customer)
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "users"
