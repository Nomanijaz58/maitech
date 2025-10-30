from fastapi import APIRouter, Depends
from app.utils.auth import verify_cognito_user

router = APIRouter(prefix="/api", tags=["Reports"])


@router.get("/student/reports/time-tracking", summary="Time tracking report")
async def time_tracking(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "student/reports/time-tracking"}


@router.get("/student/reports/academic-performance", summary="Academic performance report")
async def academic_performance(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "student/reports/academic-performance"}


@router.get("/student/reports/topics-summary", summary="Topics summary report")
async def topics_summary(user = Depends(verify_cognito_user)):
    return {"message": "Success", "endpoint": "student/reports/topics-summary"}


