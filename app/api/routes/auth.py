from fastapi import APIRouter, HTTPException, status
import asyncio
from app.core.cognito import sign_up, confirm_sign_up, login
from app.schemas.user_schemas import RegisterRequest, ConfirmUserRequest, LoginRequest
from app.db.documents.user import User
from app.db.database import db_service


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    try:
        # 1) Register in Cognito
        await asyncio.to_thread(sign_up, payload.email, payload.password, payload.name)
    except ValueError as e:
        return {"status": "error", "detail": str(e)}

    # 2) Persist in MongoDB using pymongo
    user = await asyncio.to_thread(db_service.find_user_by_email, payload.email)
    if user is None:
        user = User(email=payload.email, full_name=payload.name, role=payload.role)
        created_user = await asyncio.to_thread(db_service.create_user, user)
        if not created_user:
            return {"status": "error", "detail": "Failed to create user in database"}

    return {"status": "success", "message": "User registered. Please check your email for the confirmation code."}


@router.post("/confirm", status_code=status.HTTP_200_OK)
async def confirm(payload: ConfirmUserRequest):
    try:
        await asyncio.to_thread(confirm_sign_up, payload.email, payload.code)
        return {"status": "success", "message": "User confirmed successfully."}
    except ValueError as e:
        return {"status": "error", "detail": str(e)}


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(payload: LoginRequest):
    try:
        # Authenticate with Cognito
        auth_result = await asyncio.to_thread(login, payload.email, payload.password)
        
        # Get user from MongoDB using pymongo
        user = await asyncio.to_thread(db_service.find_user_by_email, payload.email)
        
        # If user doesn't exist in MongoDB but is authenticated in Cognito, create them
        if not user:
            print(f"User {payload.email} authenticated in Cognito but not found in MongoDB. Creating user record...")
            
            # Extract user info from Cognito ID token if available
            id_token = auth_result.get("AuthenticationResult", {}).get("IdToken")
            user_name = payload.email.split('@')[0]  # Default name from email
            user_role = "customer"  # Default role
            
            # Try to get user info from Cognito if possible
            try:
                # You could decode the ID token to get user attributes, but for now use defaults
                pass
            except Exception as e:
                print(f"Could not extract user info from ID token: {e}")
            
            # Create user in MongoDB
            new_user = User(email=payload.email, full_name=user_name, role=user_role)
            created_user = await asyncio.to_thread(db_service.create_user, new_user)
            
            if created_user:
                user = created_user
                print(f"✅ Created user record for {payload.email}")
            else:
                print(f"❌ Failed to create user record for {payload.email}")
                return {"status": "error", "detail": "Failed to create user record in database"}
        
        # Extract tokens from Cognito response
        authentication_result = auth_result.get("AuthenticationResult", {})
        access_token = authentication_result.get("AccessToken")
        refresh_token = authentication_result.get("RefreshToken")
        id_token = authentication_result.get("IdToken")
        
        return {
            "status": "success",
            "message": "Login successful",
            "user": {
                "email": user.email,
                "name": user.full_name,
                "role": user.role
            },
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "id_token": id_token
            }
        }
    except ValueError as e:
        error_message = str(e)
        print(f"Login error: {error_message}")
        
        # Handle specific Cognito errors
        if "Incorrect username or password" in error_message:
            return {"status": "error", "detail": "Invalid email or password. Please check your credentials."}
        elif "UserNotFoundException" in error_message:
            return {"status": "error", "detail": "User not found. Please register first."}
        elif "NotAuthorizedException" in error_message:
            return {"status": "error", "detail": "Account not confirmed. Please check your email for confirmation code."}
        else:
            return {"status": "error", "detail": error_message}






