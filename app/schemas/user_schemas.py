from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.db.documents.user import UserRole


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole = UserRole.customer


class ConfirmUserRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=10)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)






