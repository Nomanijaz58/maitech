from fastapi import APIRouter, HTTPException, status
import asyncio
from app.core.cognito import sign_up, confirm_sign_up
from app.schemas.user_schemas import RegisterRequest, ConfirmUserRequest
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
    created_id = None
    role_value = payload.role
    if user is None:
        user = User(email=payload.email, full_name=payload.name, role=payload.role)
        created_user = await asyncio.to_thread(db_service.create_user, user)
        if not created_user:
            return {"status": "error", "detail": "Failed to create user in database"}
        created_id = str(created_user.id)
        role_value = str(created_user.role)
    else:
        created_id = str(user.id)
        role_value = str(user.role)

    return {
        "status": "success",
        "message": "User registered. Please check your email for the confirmation code.",
        "user_id": created_id,
        "role": role_value,
    }


@router.post("/confirm", status_code=status.HTTP_200_OK)
async def confirm(payload: ConfirmUserRequest):
    try:
        await asyncio.to_thread(confirm_sign_up, payload.email, payload.code)
        return {"status": "success", "message": "User confirmed successfully."}
    except ValueError as e:
        return {"status": "error", "detail": str(e)}


# Login API removed as per requirements






