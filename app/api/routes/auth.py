from fastapi import APIRouter, HTTPException, status
from app.core.cognito import sign_up, confirm_sign_up
from app.schemas.user_schemas import RegisterRequest, ConfirmUserRequest
from app.db.documents.user import User


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    """
    Register a new user in AWS Cognito and MongoDB using Beanie.
    """
    try:
        # 1) Register in Cognito (synchronous operation, wrapped in asyncio.to_thread if needed)
        import asyncio
        await asyncio.to_thread(sign_up, payload.email, payload.password, payload.name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # 2) Check if user exists in MongoDB using Beanie
    existing_user = await User.find_one(User.email == payload.email)
    
    if existing_user:
        # User already exists, return existing user info
        return {
            "status": "success",
            "message": "User already exists.",
            "user_id": str(existing_user.id),
            "role": str(existing_user.role),
        }
    
    # 3) Create new user in MongoDB using Beanie
    try:
        new_user = User(
            email=payload.email,
            full_name=payload.name,
            role=payload.role
        )
        await new_user.insert()
        
        return {
            "status": "success",
            "message": "User registered. Please check your email for the confirmation code.",
            "user_id": str(new_user.id),
            "role": str(new_user.role),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user in database: {str(e)}"
        )


@router.post("/confirm", status_code=status.HTTP_200_OK)
async def confirm(payload: ConfirmUserRequest):
    """
    Confirm user sign-up with verification code.
    """
    try:
        import asyncio
        await asyncio.to_thread(confirm_sign_up, payload.email, payload.code)
        return {"status": "success", "message": "User confirmed successfully."}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Login API removed as per requirements






