"""
User routes using Beanie ODM for all database operations.

This module uses Beanie's async methods for all MongoDB operations.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId

from app.models.user_model import UserCreate, UserResponse
from app.db.documents.user import User as UserDocument

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """
    Create a new user using Beanie ODM.
    """
    try:
        # Check if user already exists
        existing_user = await UserDocument.find_one(UserDocument.email == user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user using Beanie
        new_user = UserDocument(
            email=user_data.email,
            full_name=user_data.name,
            role=user_data.role
        )
        await new_user.insert()
        
        return {
            "status": "success",
            "message": "User created successfully",
            "user_id": str(new_user.id)
        }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user: {str(e)}"
        )


@router.get("/", response_model=List[UserResponse])
async def get_all_users(limit: int = 100):
    """
    Get all users from the database using Beanie ODM.
    """
    try:
        # Query using Beanie async methods
        users = await UserDocument.find_all().limit(limit).to_list()
        
        # Convert to response format
        formatted_users = []
        for user in users:
            formatted_user = {
                "id": str(user.id),
                "name": user.full_name or "Unknown",
                "email": user.email,
                "role": str(user.role),
                "created_at": user.created_at
            }
            formatted_users.append(formatted_user)
        
        return formatted_users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str):
    """
    Get a specific user by ID using Beanie ODM.
    """
    try:
        # Validate ObjectId format
        try:
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Query using Beanie async methods
        user = await UserDocument.get(object_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Format response
        return {
            "id": str(user.id),
            "name": user.full_name or "Unknown",
            "email": user.email,
            "role": str(user.role),
            "created_at": user.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}"
        )
