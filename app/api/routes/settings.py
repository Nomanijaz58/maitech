from fastapi import APIRouter, Depends
from app.utils.auth import verify_cognito_user

router = APIRouter(prefix="/api", tags=["Settings"])


@router.get("/user/personal-info", summary="Get personal info")
async def get_personal_info(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "user/personal-info"}


@router.put("/user/personal-info", summary="Update personal info")
async def update_personal_info(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "user/personal-info"}


@router.get("/user/tutor-customization", summary="Get tutor customization")
async def get_tutor_customization(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "user/tutor-customization"}


@router.put("/user/tutor-customization", summary="Update tutor customization")
async def update_tutor_customization(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "user/tutor-customization"}


@router.get("/user/preferences", summary="Get user preferences")
async def get_preferences(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "user/preferences"}


@router.put("/user/preferences", summary="Update user preferences")
async def update_preferences(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "user/preferences"}


@router.get("/user/system-settings", summary="Get system settings")
async def get_system_settings(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "user/system-settings"}


@router.put("/user/system-settings", summary="Update system settings")
async def update_system_settings(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "user/system-settings"}


@router.patch("/user/avatar", summary="Update user avatar")
async def patch_avatar(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "user/avatar"}


@router.post("/user/change-password", summary="Change password")
async def change_password(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "user/change-password"}


@router.put("/user/2fa", summary="Update 2FA settings")
async def update_two_factor(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "user/2fa"}


@router.get("/user/login-history", summary="Get login history")
async def get_login_history(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "user/login-history"}


