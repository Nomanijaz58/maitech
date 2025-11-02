from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Reports"])


@router.get("/student/reports/time-tracking", summary="Time tracking report")
async def time_tracking():
    return {"message": "Success", "endpoint": "student/reports/time-tracking"}


@router.get("/student/reports/academic-performance", summary="Academic performance report")
async def academic_performance():
    return {"message": "Success", "endpoint": "student/reports/academic-performance"}


@router.get("/student/reports/topics-summary", summary="Topics summary report")
async def topics_summary():
    return {"message": "Success", "endpoint": "student/reports/topics-summary"}


