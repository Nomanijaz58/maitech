"""
User routes using Beanie models for validation and PyMongo for database operations.

This module demonstrates the hybrid approach:
- Beanie models are used for schema definition and validation
- PyMongo client is used for actual database operations
- No async Beanie CRUD methods are used
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId

from app.models.user_model import User, UserCreate, UserResponse
from app.db.mongo_client import db

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """
    Create a new user.
    
    Uses Beanie model for validation and PyMongo for database insertion.
    """
    try:
        # Create User instance for validation (Beanie/Pydantic)
        user = User(
            name=user_data.name,
            email=user_data.email,
            role=user_data.role
        )
        
        # Convert to dict for PyMongo insertion
        user_dict = user.model_dump()
        
        # Insert using PyMongo (synchronous operation)
        result = db["users"].insert_one(user_dict)
        
        if result.inserted_id:
            return {
                "status": "success",
                "message": "User created successfully",
                "user_id": str(result.inserted_id)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user: {str(e)}"
        )


@router.get("/", response_model=List[UserResponse])
async def get_all_users():
    """
    Get all users from the database.
    
    Uses PyMongo for database query and Beanie model for response validation.
    """
    try:
        # Query using PyMongo (synchronous operation)
        users_cursor = db["users"].find()
        users = list(users_cursor)
        
        # Convert ObjectId to string and format response
        formatted_users = []
        for user in users:
            formatted_user = {
                "id": str(user["_id"]),
                "name": user.get("name", user.get("full_name", "Unknown")),
                "email": user["email"],
                "role": user["role"],
                "created_at": user["created_at"]
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
    Get a specific user by ID.
    
    Uses PyMongo for database query and Beanie model for response validation.
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
        
        # Query using PyMongo (synchronous operation)
        user = db["users"].find_one({"_id": object_id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Format response
        return {
            "id": str(user["_id"]),
            "name": user.get("name", user.get("full_name", "Unknown")),
            "email": user["email"],
            "role": user["role"],
            "created_at": user["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}"
        )
