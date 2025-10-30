from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter(
    prefix='/api/student',
    tags=['Student']
)

# ------------------------
# 📊 DASHBOARD API
# ------------------------
@router.get('/dashboard', summary='Get student dashboard data')
async def get_student_dashboard():
    return {
        'userId': 'demo-user-123',
        'progress': 85,
        'weekly_activity': [60, 75, 80, 90, 100],
        'subjects': [
            {'name': 'Math', 'progress': 90},
            {'name': 'Science', 'progress': 80},
            {'name': 'English', 'progress': 85}
        ],
        'recommendations': ['Revise Algebra', 'Watch Physics Lecture 3']
    }

# ------------------------
# 🧭 LEARNING PATH API
# ------------------------
@router.get('/learning-path', summary='Fetch personalized learning path')
async def get_learning_path():
    return {
        'userId': 'demo-user-123',
        'paths': [
            {'subject': 'Math', 'modules': 8, 'completed': 5},
            {'subject': 'Science', 'modules': 10, 'completed': 7}
        ],
        'progress_chart': {
            'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'data': [70, 75, 80, 85]
        },
        'achievements': [
            {'title': 'Top 10% in Class', 'date': '2025-10-01'},
            {'title': 'Completed Science Path', 'date': '2025-09-20'}
        ]
    }

# ------------------------
# 📘 LESSONS API
# ------------------------
@router.get('/lessons', summary='Fetch all available lessons')
async def get_lessons():
    return {
        'lessons': [
            {'lesson_id': 'L001', 'title': 'Photosynthesis', 'status': 'In Progress'},
            {'lesson_id': 'L002', 'title': 'Newton\'s Laws', 'status': 'Completed'}
        ]
    }

@router.get('/lessons/history', summary='Fetch lesson history')
async def get_lesson_history():
    return {
        'history': [
            {'lesson_id': 'L002', 'title': 'Newton\'s Laws', 'completed_on': '2025-10-10', 'score': 92},
            {'lesson_id': 'L003', 'title': 'Periodic Table', 'completed_on': '2025-09-28', 'score': 88}
        ]
    }

@router.get('/lessons/{lesson_id}', summary='Fetch detailed lesson view')
async def get_lesson_details(lesson_id: str):
    lessons = {
        'L001': {
            'title': 'Photosynthesis',
            'content': [
                {'type': 'text', 'message': 'What is the process by which plants make food?'},
                {'type': 'student', 'message': 'Photosynthesis!'},
                {'type': 'text', 'message': 'Correct! Plants use sunlight to convert CO2 and water into glucose.'}
            ],
            'status': 'In Progress',
            'score': None
        },
        'L002': {
            'title': 'Newton\'s Laws',
            'content': [
                {'type': 'text', 'message': 'What is inertia?'},
                {'type': 'student', 'message': 'Resistance to motion change.'},
                {'type': 'text', 'message': 'Excellent! That\'s Newton\'s First Law.'}
            ],
            'status': 'Completed',
            'score': 92
        }
    }
    lesson = lessons.get(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail='Lesson not found')
    return lesson
