"""
Forgot Password API routes for MaiTech
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.auth_schemas import (
    ForgotPasswordRequest, 
    VerifyOTPRequest, 
    ResetPasswordRequest,
    OTPResponse,
    PasswordResetResponse
)
from app.services.otp_service import OTPService
from app.services.mail import send_email
from app.core.cognito import reset_password, confirm_forgot_password
from app.db.mongo_client import db
import asyncio

router = APIRouter(prefix="/api/auth", tags=["forgot-password"])


@router.post("/forgot-password", response_model=OTPResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Step 1: Send OTP to user's email for password reset
    
    This endpoint initiates the forgot password flow by:
    1. Checking if user exists in Cognito
    2. Calling Cognito's forgot_password to send OTP via email
    3. Storing OTP tracking record in database
    """
    try:
        email = request.email.lower()
        
        # Check if user exists in Cognito and initiate password reset
        try:
            # Initiate password reset in Cognito - this will send OTP via email
            cognito_response = await asyncio.to_thread(reset_password, email)
            print(f"Cognito forgot password response: {cognito_response}")
            
            # Check if email was actually sent
            delivery_details = cognito_response.get("CodeDeliveryDetails", {})
            delivery_medium = delivery_details.get("DeliveryMedium", "")
            destination = delivery_details.get("Destination", "")
            
            if delivery_medium != "EMAIL":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email delivery failed. Delivery medium: {delivery_medium}"
                )
            
            # Store a placeholder OTP record to track the flow
            # The actual OTP will be verified through Cognito
            otp = "COGNITO_OTP"  # Placeholder to indicate Cognito OTP
            otp_info = OTPService.store_otp(email, otp)
            
            # Mask email for security
            masked_email = f"{email[:2]}***{email[email.find('@'):]}" if '@' in email else email
            
            return OTPResponse(
                status="success",
                message=f"OTP has been sent to {masked_email}. Please check your email (including spam folder).",
                expires_in=otp_info["expires_in_seconds"]
            )
            
        except Exception as e:
            error_message = str(e)
            print(f"Cognito forgot password failed: {error_message}")
            
            # Handle specific Cognito errors
            if "Attempt limit exceeded" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many password reset attempts. Please wait 15 minutes before trying again."
                )
            elif "User does not exist" in error_message or "UserNotFoundException" in error_message:
                # For security, don't reveal if user exists or not
                return OTPResponse(
                    status="success",
                    message="If an account with this email exists, an OTP has been sent.",
                    expires_in=OTPService.OTP_EXPIRY_MINUTES * 60
                )
            elif "InvalidParameterException" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email format or Cognito configuration issue."
                )
            elif "UnrecognizedClientException" in error_message or "InvalidUserPoolConfigurationException" in error_message:
                # AWS credentials or configuration issue - use fallback
                print("⚠️ Cognito authentication failed, using fallback OTP system")
                try:
                    # Generate custom OTP as fallback
                    otp = OTPService.generate_otp()
                    otp_info = OTPService.store_otp(email, otp)
                    
                    # Try to send email via SendGrid
                    try:
                        await send_email(
                            to_email=email,
                            subject="Password Reset OTP - MaiTech",
                            html_content=f"""
                            <h2>Password Reset Request</h2>
                            <p>Your OTP for password reset is: <strong>{otp}</strong></p>
                            <p>This OTP will expire in 10 minutes.</p>
                            <p>If you didn't request this, please ignore this email.</p>
                            """
                        )
                        print("✅ Fallback email sent successfully!")
                    except Exception as email_error:
                        print(f"⚠️ Fallback email failed: {email_error}")
                        print(f"📱 OTP for manual testing: {otp}")
                    
                    # Mask email for security
                    masked_email = f"{email[:2]}***{email[email.find('@'):]}" if '@' in email else email
                    
                    return OTPResponse(
                        status="success",
                        message=f"OTP has been sent to {masked_email}. Please check your email (including spam folder).",
                        expires_in=otp_info["expires_in_seconds"]
                    )
                except Exception as fallback_error:
                    print(f"❌ Fallback OTP system failed: {fallback_error}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Email delivery service is temporarily unavailable. Please try again later."
                    )
            else:
                # For other errors, return generic message for security
                return OTPResponse(
                    status="success",
                    message="If an account with this email exists, an OTP has been sent.",
                    expires_in=OTPService.OTP_EXPIRY_MINUTES * 60
                )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process forgot password request: {str(e)}"
        )


@router.post("/verify-otp", response_model=OTPResponse)
async def verify_otp(request: VerifyOTPRequest):
    """
    Step 2: Verify the 6-digit OTP
    
    This endpoint verifies the OTP sent to user's email.
    For Cognito OTP flow, we just store the OTP for later use in password reset.
    """
    try:
        email = request.email.lower()
        otp = request.otp.strip()
        
        # Validate OTP format
        if not otp.isdigit() or len(otp) != 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP must be a 6-digit number"
            )
        
        # Check if we have a Cognito OTP flow
        otp_record = db.otps.find_one({"email": email, "verified": False})
        
        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active OTP found for this email. Please request a new OTP."
            )
        
        if otp_record["otp"] == "COGNITO_OTP":
            # This is a Cognito OTP flow - store the OTP for password reset
            db.otps.update_one(
                {"_id": otp_record["_id"]},
                {"$set": {"verified": True, "cognito_otp": otp}}
            )
            
            return OTPResponse(
                status="success",
                message="OTP verified successfully. You can now reset your password."
            )
        else:
            # Use our custom OTP verification (for fallback system)
            verification_result = OTPService.verify_otp(email, otp)
            
            if verification_result["valid"]:
                # Mark as verified for password reset
                db.otps.update_one(
                    {"_id": otp_record["_id"]},
                    {"$set": {"verified": True}}
                )
                
                return OTPResponse(
                    status="success",
                    message="OTP verified successfully. You can now reset your password."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=verification_result["message"]
                )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify OTP: {str(e)}"
        )


@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password_endpoint(request: ResetPasswordRequest):
    """
    Step 3: Reset password with new password after OTP verification
    
    This endpoint completes the password reset process by:
    1. Verifying the OTP again
    2. Updating the password in Cognito
    3. Cleaning up the OTP record
    """
    try:
        email = request.email.lower()
        otp = request.otp.strip()
        new_password = request.new_password
        
        # Validate OTP format
        if not otp.isdigit() or len(otp) != 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP must be a 6-digit number"
            )
        
        # Check if we have a verified OTP record
        otp_record = db.otps.find_one({"email": email, "verified": True})
        
        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No verified OTP found for this email. Please verify OTP first."
            )
        
        # Check if this is a Cognito OTP or fallback OTP
        if otp_record.get("cognito_otp"):
            # This is a Cognito OTP flow
            cognito_otp = otp_record.get("cognito_otp", otp)
            
            # Reset password in Cognito
            try:
                await asyncio.to_thread(confirm_forgot_password, email, cognito_otp, new_password)
            except Exception as e:
                error_message = str(e)
                print(f"Cognito password reset failed: {error_message}")
                
                if "Invalid verification code" in error_message:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid or expired OTP. Please request a new OTP and try again."
                    )
                elif "CodeMismatchException" in error_message:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid OTP. Please check the code and try again."
                    )
                elif "ExpiredCodeException" in error_message:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="OTP has expired. Please request a new OTP."
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to reset password: {error_message}"
                    )
        else:
            # This is a fallback OTP system - we can't actually reset password in Cognito
            # For now, just return success (in production, you'd need to implement password reset differently)
            print("⚠️ Fallback OTP system - password reset not implemented for Cognito")
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Password reset is temporarily unavailable. Please contact support or try again later when Cognito is available."
            )
        
        # Clean up OTP record
        db.otps.delete_many({"email": email})
        
        return PasswordResetResponse(
            status="success",
            message="Password has been reset successfully. You can now login with your new password."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )


@router.get("/otp-status/{email}")
async def get_otp_status(email: str):
    """
    Get OTP status for an email (for frontend countdown timer)
    """
    try:
        email = email.lower()
        otp_info = OTPService.get_otp_info(email)
        
        if not otp_info:
            return {
                "status": "not_found",
                "message": "No active OTP found for this email"
            }
        
        # Calculate remaining time
        from datetime import datetime
        remaining_seconds = int((otp_info["expires_at"] - datetime.utcnow()).total_seconds())
        
        return {
            "status": "active",
            "expires_in_seconds": max(0, remaining_seconds),
            "attempts": otp_info["attempts"],
            "remaining_attempts": otp_info["remaining_attempts"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OTP status: {str(e)}"
        )
