from beanie import Document
from pydantic import EmailStr, Field, ConfigDict, field_serializer
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


class User(Document):
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.student)
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "users"  # Collection name in MongoDB
        
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
    
    @field_serializer('id')
    def serialize_objectid(self, oid: ObjectId, _info) -> str:
        """Serialize ObjectId to string"""
        return str(oid)
