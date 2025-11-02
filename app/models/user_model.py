"""
User model using Pydantic BaseModel for schema definition and validation.

This module defines the User model using Pydantic BaseModel for schema validation.
Pydantic is used for schema definition, validation, and serialization.
All actual database operations are performed using PyMongo client.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_serializer
from typing import Optional
from enum import Enum
from datetime import datetime, timezone


class UserRole(str, Enum):
    """User role enumeration."""
    customer = "customer"
    seller = "seller"
    admin = "admin"


class User(BaseModel):
    """
    User model using Pydantic BaseModel for schema definition.
    
    This model is used for:
    - Schema validation using Pydantic
    - Type hints and IDE support
    - Data serialization/deserialization
    
    Database operations are performed using PyMongo client.
    """
    
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    role: UserRole = Field(default=UserRole.customer, description="User's role")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(
        # Allow field name aliases
        populate_by_name=True,
    )
    
    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        """Serialize datetime to ISO format"""
        return dt.isoformat()


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role: UserRole = Field(default=UserRole.customer)


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    name: str
    email: str
    role: UserRole
    created_at: datetime
    
    model_config = ConfigDict()
    
    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        """Serialize datetime to ISO format"""
        return dt.isoformat()
