from beanie import Document, PydanticObjectId
from pydantic import EmailStr
from datetime import datetime, timezone
from typing import Optional


class User(Document):
    email: EmailStr
    hashed_password: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_verified: bool = False
    created_at: datetime = datetime.now(timezone.utc)
    two_step_auth_enabled: bool = True
    active_workspace_id: Optional[PydanticObjectId] = None
    is_admin: bool = False

    class Settings:
        name = "users"
