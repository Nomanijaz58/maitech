from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Literal


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)
    role: Literal["student", "teacher", "parent", "school_manager"] = "student"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "TestPass123!",
                "role": "student",
            }
        }
    )


class ConfirmUserRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=10)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)






