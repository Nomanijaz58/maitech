from fastapi import APIRouter, HTTPException, status
import asyncio
from beanie import PydanticObjectId
from app.core.cognito import sign_up, confirm_sign_up
from app.schemas.user_schemas import RegisterRequest, ConfirmUserRequest
from app.db.documents.user import User


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    try:
        # 1) Register in Cognito
        await asyncio.to_thread(sign_up, payload.email, payload.password, payload.name)
    except ValueError as e:
        return {"status": "error", "detail": str(e)}

    # 2) Persist in MongoDB (Beanie)
    user = await User.find_one(User.email == payload.email)
    if user is None:
        user = User(email=payload.email, full_name=payload.name, role=payload.role)
        await user.insert()

    return {"status": "success", "message": "User registered. Please check your email for the confirmation code."}


@router.post("/confirm", status_code=status.HTTP_200_OK)
async def confirm(payload: ConfirmUserRequest):
    try:
        await asyncio.to_thread(confirm_sign_up, payload.email, payload.code)
        return {"status": "success", "message": "User confirmed successfully."}
    except ValueError as e:
        return {"status": "error", "detail": str(e)}


