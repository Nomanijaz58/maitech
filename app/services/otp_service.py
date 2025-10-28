"""
OTP (One-Time Password) service for MaiTech API
"""

import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict
from app.db.mongo_client import db


class OTPService:
    """Service for generating, storing, and verifying OTPs"""
    
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 10  # OTP expires in 10 minutes
    MAX_ATTEMPTS = 3  # Maximum verification attempts
    
    @classmethod
    def generate_otp(cls) -> str:
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=cls.OTP_LENGTH))
    
    @classmethod
    def store_otp(cls, email: str, otp: str) -> Dict:
        """Store OTP in database with expiry time"""
        expires_at = datetime.utcnow() + timedelta(minutes=cls.OTP_EXPIRY_MINUTES)
        
        otp_data = {
            "email": email,
            "otp": otp,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "attempts": 0,
            "verified": False
        }
        
        # Remove any existing OTP for this email
        db.otps.delete_many({"email": email})
        
        # Insert new OTP
        result = db.otps.insert_one(otp_data)
        
        return {
            "otp_id": str(result.inserted_id),
            "expires_at": expires_at,
            "expires_in_seconds": cls.OTP_EXPIRY_MINUTES * 60
        }
    
    @classmethod
    def verify_otp(cls, email: str, otp: str) -> Dict:
        """Verify OTP for given email"""
        # Find the OTP record
        otp_record = db.otps.find_one({
            "email": email,
            "verified": False
        })
        
        if not otp_record:
            return {
                "valid": False,
                "message": "No OTP found for this email or OTP already used"
            }
        
        # Check if OTP has expired
        if datetime.utcnow() > otp_record["expires_at"]:
            # Clean up expired OTP
            db.otps.delete_one({"_id": otp_record["_id"]})
            return {
                "valid": False,
                "message": "OTP has expired"
            }
        
        # Check if max attempts exceeded
        if otp_record["attempts"] >= cls.MAX_ATTEMPTS:
            # Clean up OTP after max attempts
            db.otps.delete_one({"_id": otp_record["_id"]})
            return {
                "valid": False,
                "message": "Maximum verification attempts exceeded"
            }
        
        # Increment attempts
        db.otps.update_one(
            {"_id": otp_record["_id"]},
            {"$inc": {"attempts": 1}}
        )
        
        # Verify OTP
        if otp_record["otp"] == otp:
            # Mark as verified
            db.otps.update_one(
                {"_id": otp_record["_id"]},
                {"$set": {"verified": True}}
            )
            return {
                "valid": True,
                "message": "OTP verified successfully"
            }
        else:
            remaining_attempts = cls.MAX_ATTEMPTS - (otp_record["attempts"] + 1)
            return {
                "valid": False,
                "message": f"Invalid OTP. {remaining_attempts} attempts remaining"
            }
    
    @classmethod
    def cleanup_expired_otps(cls):
        """Clean up expired OTPs from database"""
        result = db.otps.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        return result.deleted_count
    
    @classmethod
    def get_otp_info(cls, email: str) -> Optional[Dict]:
        """Get OTP information for an email"""
        otp_record = db.otps.find_one({
            "email": email,
            "verified": False
        })
        
        if not otp_record:
            return None
        
        if datetime.utcnow() > otp_record["expires_at"]:
            # Clean up expired OTP
            db.otps.delete_one({"_id": otp_record["_id"]})
            return None
        
        return {
            "email": otp_record["email"],
            "created_at": otp_record["created_at"],
            "expires_at": otp_record["expires_at"],
            "attempts": otp_record["attempts"],
            "remaining_attempts": cls.MAX_ATTEMPTS - otp_record["attempts"]
        }
