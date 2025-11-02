import datetime
from fastapi import APIRouter

teacher_router = APIRouter(prefix="/api/teacher", tags=["Teacher"])


# ----------------------------------------------------------------------
# 📊 DASHBOARD
# ----------------------------------------------------------------------
@teacher_router.get("/dashboard", summary="Get teacher dashboard data")
async def get_teacher_dashboard():
    return {
        "total_classes": 5,
        "total_students": 120,
        "avg_weekly_usage": "15 hrs",
        "overall_avg_score": "85%",
        "student_performance_overview": [
            {
                "student_name": "Ethan Harper",
                "class": "Mathematics",
                "assigned_parents": "John Doe",
                "attendance": "95%",
                "assignment_complete": "72%",
                "average_score": "88%",
            }
        ],
        "class_statistics": [
            {"subject": "Mathematics", "grade": "Grade 10", "students": 30},
            {"subject": "English Literature", "grade": "Grade 10", "students": 30},
        ],
        "tips_recommendations": [
            {
                "title": "Boost Engagement with Interactive Quizzes",
                "content": "Try gamified learning for student retention.",
            }
        ],
    }


# ----------------------------------------------------------------------
# 🏫 CLASSES
# ----------------------------------------------------------------------
@teacher_router.get("/classes", summary="Get teacher classes")
async def get_teacher_classes():
    return [
        {
            "class_name": "10",
            "subject": "Mathematics",
            "weekly_time": "5 hours",
            "average_score": "88%",
            "students": 25,
            "performance": "Excellent",
            "status": "On Track",
        }
    ]


@teacher_router.get("/classes/{class_id}", summary="Get class details")
async def get_class_details(class_id: str):
    return {
        "class_id": class_id,
        "subject": "Mathematics",
        "students": [
            {
                "student_name": "Ethan Harper",
                "attendance": "95%",
                "assignments_completed": 8,
                "average_score": "85%",
            }
        ],
    }


@teacher_router.post("/classes/{class_id}/assignments", summary="Add new assignment")
async def create_assignment(
    class_id: str,
    payload: dict,
):
    return {
        "message": "Assignment created successfully",
        "class_id": class_id,
        "assignment": payload,
    }


@teacher_router.get("/classes/{class_id}/assignments", summary="Get class assignments")
async def get_class_assignments(class_id: str):
    return [
        {
            "assignment_id": "asg_001",
            "title": "Chapter 5 Algebra Practice",
            "due_date": "2025-11-10",
            "completion_rate": "82%",
        }
    ]


@teacher_router.post("/classes/{class_id}/grades", summary="Upload or update grades")
async def update_grades(class_id: str, payload: dict):
    return {"message": "Grades updated successfully", "class_id": class_id, "grades": payload}


# ----------------------------------------------------------------------
# 📈 REPORTS
# ----------------------------------------------------------------------
@teacher_router.get("/reports/class-performance", summary="Get class performance report")
async def get_teacher_reports():
    return {
        "overall_avg_score": 85,
        "top_subjects": [
            {"name": "Mathematics", "score": 90},
            {"name": "Science", "score": 88},
        ],
        "weak_subjects": [{"name": "History", "score": 70}],
        "attendance_summary": {
            "avg_attendance": 92,
            "best_class": "Grade 10 Math",
        },
    }


# ----------------------------------------------------------------------
# 🧑‍🏫 CLASS CHAT (shared with student)
# ----------------------------------------------------------------------
@teacher_router.get("/class-chat/conversations", summary="List class conversations")
async def get_class_chats():
    return [
        {"chat_id": "math_9", "subject": "Math", "messages_count": 12, "unread": 2},
        {"chat_id": "science_10", "subject": "Science", "messages_count": 5, "unread": 0},
    ]


@teacher_router.get("/class-chat/conversation/{chat_id}/messages", summary="Get chat messages")
async def get_chat_messages(chat_id: str):
    return [
        {"sender": "Teacher", "message": "Hi everyone!", "timestamp": datetime.datetime.utcnow()},
        {"sender": "Student", "message": "Hello!", "timestamp": datetime.datetime.utcnow()},
    ]


@teacher_router.post("/class-chat/conversation/{chat_id}/message", summary="Send a new message")
async def post_chat_message(chat_id: str, payload: dict):
    return {"message": "Message sent successfully", "chat_id": chat_id, "payload": payload}


# ----------------------------------------------------------------------
# ⚙️ SETTINGS (shared with student)
# ----------------------------------------------------------------------
@teacher_router.get("/settings", summary="Get teacher settings")
async def get_teacher_settings():
    return {
        "name": "Teacher",
        "email": "teacher@example.com",
        "role": "teacher",
        "preferences": {
            "language": "English",
            "theme": "light",
            "notification_enabled": True,
        },
    }

