"""
Authentication schemas for MaiTech API
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request"""
    email: EmailStr = Field(..., description="Registered email address")


class VerifyOTPRequest(BaseModel):
    """Schema for OTP verification"""
    email: EmailStr = Field(..., description="Email address")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    
    @validator('otp')
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError('OTP must contain only digits')
        return v


class ResetPasswordRequest(BaseModel):
    """Schema for resetting password with new password"""
    email: EmailStr = Field(..., description="Email address")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('otp')
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError('OTP must contain only digits')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class OTPResponse(BaseModel):
    """Response schema for OTP operations"""
    status: str
    message: str
    expires_in: Optional[int] = None  # seconds until OTP expires


class PasswordResetResponse(BaseModel):
    """Response schema for password reset"""
    status: str
    message: str
