from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from bson import ObjectId


def utc_now():
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"
    parent = "parent"
    school_manager = "school_manager"


class User(BaseModel):
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.student)
    created_at: datetime = Field(default_factory=utc_now)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
