from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from bson import ObjectId


def utc_now():
    return datetime.now(timezone.utc)


class NotificationType(str, Enum):
    """Notification type enumeration"""
    CHAT = "chat"
    FLAGGED_CONTENT = "flagged_content"
    SYSTEM = "system"


class NotificationStatus(str, Enum):
    """Notification status enumeration"""
    UNREAD = "unread"
    READ = "read"
    DISMISSED = "dismissed"


class Notification(Document):
    """Notification model for user notifications"""
    
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    user_id: str = Field(..., description="User ID from Cognito")
    title: str = Field(..., min_length=1, max_length=200, description="Notification title")
    message: str = Field(..., min_length=1, description="Notification message content")
    type: str = Field(..., description="Notification type: chat, flagged_content, or system")
    status: str = Field(default=NotificationStatus.UNREAD, description="Notification status: unread, read, or dismissed")
    created_at: datetime = Field(default_factory=utc_now, description="Timestamp when notification was created")
    related_resource_id: Optional[str] = Field(None, description="ID of related resource (e.g., alert_id for flagged content)")
    
    class Settings:
        name = "notifications"  # Collection name in MongoDB
        
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

