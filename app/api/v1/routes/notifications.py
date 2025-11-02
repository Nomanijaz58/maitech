"""
Notification and Flagged Content Management API Endpoints

This module provides endpoints for managing user notifications and flagged content.
All endpoints are public and do not require authentication.
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime

from app.db.documents.notification import Notification


router = APIRouter(prefix="/api", tags=["Notifications"])


# ============================================================================
# Pydantic Schemas for Request/Response
# ============================================================================

class NotificationResponse(BaseModel):
    """Response model for notification"""
    id: str
    user_id: str
    title: str
    message: str
    type: str
    status: str
    created_at: datetime
    related_resource_id: Optional[str] = None
    
    class Config:
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class NotificationListResponse(BaseModel):
    """Paginated response for notifications list"""
    notifications: List[NotificationResponse]
    total: int
    limit: int
    offset: int


class MarkReadRequest(BaseModel):
    """Request model for marking multiple notifications as read"""
    notification_ids: List[str] = Field(..., min_items=1, description="List of notification IDs to mark as read")


class FlaggedContentActionRequest(BaseModel):
    """Request model for flagged content action"""
    action: str = Field(..., description="Action to take: 'resolve' or 'action_taken'")
    details: Optional[str] = Field(None, description="Optional reason or details for the action")


class SuccessResponse(BaseModel):
    """Standard success response"""
    message: str
    status: str = "success"


# ============================================================================
# Notification Endpoints
# ============================================================================

@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of notifications to return"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: unread, read, or dismissed"),
    user_id: Optional[str] = Query(None, description="Optional user ID to filter notifications")
):
    """
    Fetch all notifications.
    
    Supports pagination via limit and offset parameters.
    Can filter by notification status and optional user_id.
    Returns notifications sorted by newest first.
    """
    try:
        # Build query filter
        query_filter = {}
        
        if user_id:
            query_filter["user_id"] = user_id
        
        if status_filter:
            query_filter["status"] = status_filter
        
        # Count total matching notifications
        total = await Notification.find(query_filter).count()
        
        # Fetch paginated notifications, sorted by newest first
        notifications = await Notification.find(
            query_filter
        ).sort(-Notification.created_at).skip(offset).limit(limit).to_list()
        
        # Format response
        notification_responses = [
            NotificationResponse(
                id=str(notif.id),
                user_id=notif.user_id,
                title=notif.title,
                message=notif.message,
                type=notif.type,
                status=notif.status,
                created_at=notif.created_at,
                related_resource_id=notif.related_resource_id
            )
            for notif in notifications
        ]
        
        return NotificationListResponse(
            notifications=notification_responses,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching notifications: {str(e)}"
        )


@router.patch("/notifications/mark-read", response_model=SuccessResponse)
async def mark_notifications_read(
    request: MarkReadRequest
):
    """
    Mark multiple notifications as "read".
    
    Accepts a list of notification IDs and updates their status to "read".
    """
    try:
        # Convert string IDs to ObjectIds
        notification_ids = []
        for notif_id in request.notification_ids:
            try:
                notification_ids.append(ObjectId(notif_id))
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid notification ID format: {notif_id}"
                )
        
        # Update notifications
        # Find all matching notifications first
        notifications = await Notification.find(
            Notification.id.in_(notification_ids)
        ).to_list()
        
        # Update each notification
        modified_count = 0
        for notif in notifications:
            if notif.status != "read":
                notif.status = "read"
                await notif.save()
                modified_count += 1
        
        if modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching notifications found or already marked as read"
            )
        
        return SuccessResponse(
            message=f"Successfully marked {modified_count} notification(s) as read"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating notifications: {str(e)}"
        )


@router.patch("/notifications/{notification_id}/read", response_model=SuccessResponse)
async def mark_notification_read(
    notification_id: str
):
    """
    Mark one specific notification as "read".
    
    Updates the notification status to "read".
    """
    try:
        # Validate ObjectId format
        try:
            object_id = ObjectId(notification_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid notification ID format"
            )
        
        # Find notification
        notification = await Notification.find_one(
            Notification.id == object_id
        )
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Update status
        notification.status = "read"
        await notification.save()
        
        return SuccessResponse(
            message="Notification marked as read successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating notification: {str(e)}"
        )


@router.delete("/notifications/{notification_id}/dismiss", response_model=SuccessResponse)
async def dismiss_notification(
    notification_id: str
):
    """
    Delete or soft-delete a specific notification.
    
    Soft deletes by setting status to "dismissed".
    """
    try:
        # Validate ObjectId format
        try:
            object_id = ObjectId(notification_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid notification ID format"
            )
        
        # Find notification
        notification = await Notification.find_one(
            Notification.id == object_id
        )
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Soft delete by setting status to dismissed
        notification.status = "dismissed"
        await notification.save()
        
        return SuccessResponse(
            message="Notification dismissed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error dismissing notification: {str(e)}"
        )


@router.get("/notifications/search", response_model=NotificationListResponse)
async def search_notifications(
    query: str = Query(..., min_length=1, description="Search query text"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    user_id: Optional[str] = Query(None, description="Optional user ID to filter search results")
):
    """
    Search notifications where title or message contains the query text.
    
    Performs case-insensitive search on notification title and message fields.
    Returns paginated results sorted by newest first.
    """
    try:
        # Build MongoDB filter with regex for case-insensitive search
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"message": {"$regex": query, "$options": "i"}}
            ]
        }
        
        if user_id:
            search_filter["user_id"] = user_id
        
        # Count total matching notifications
        total = await Notification.find(search_filter).count()
        
        # Fetch paginated notifications, sorted by newest first
        notifications = await Notification.find(
            search_filter
        ).sort(-Notification.created_at).skip(offset).limit(limit).to_list()
        
        # Format response
        notification_responses = [
            NotificationResponse(
                id=str(notif.id),
                user_id=notif.user_id,
                title=notif.title,
                message=notif.message,
                type=notif.type,
                status=notif.status,
                created_at=notif.created_at,
                related_resource_id=notif.related_resource_id
            )
            for notif in notifications
        ]
        
        return NotificationListResponse(
            notifications=notification_responses,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching notifications: {str(e)}"
        )


# ============================================================================
# Flagged Content Endpoints
# ============================================================================

@router.post("/flagged-content/{alert_id}/ignore", response_model=SuccessResponse)
async def ignore_flagged_content(
    alert_id: str
):
    """
    Mark the related flagged content notification as ignored.
    
    Updates the notification status to "dismissed" for the flagged content alert.
    """
    try:
        # Find notification related to this alert_id
        notification = await Notification.find_one(
            Notification.type == "flagged_content",
            Notification.related_resource_id == alert_id
        )
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flagged content notification not found"
            )
        
        # Update status to dismissed (ignored)
        notification.status = "dismissed"
        await notification.save()
        
        return SuccessResponse(
            message=f"Flagged content alert {alert_id} has been ignored"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ignoring flagged content: {str(e)}"
        )


@router.post("/flagged-content/{alert_id}/action", response_model=SuccessResponse)
async def take_action_on_flagged_content(
    alert_id: str,
    request: FlaggedContentActionRequest
):
    """
    Mark the flagged content as "resolved" or "action_taken".
    
    Updates the notification and marks appropriate action.
    Accepts action type and optional details.
    """
    try:
        # Validate action
        valid_actions = ["resolve", "action_taken"]
        if request.action not in valid_actions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action. Must be one of: {', '.join(valid_actions)}"
            )
        
        # Find notification related to this alert_id
        notification = await Notification.find_one(
            Notification.type == "flagged_content",
            Notification.related_resource_id == alert_id
        )
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flagged content notification not found"
            )
        
        # Update notification - mark as read and add action details to message if provided
        notification.status = "read"
        if request.details:
            notification.message += f" | Action: {request.action} - {request.details}"
        else:
            notification.message += f" | Action: {request.action}"
        await notification.save()
        
        action_message = f"Flagged content alert {alert_id} marked as {request.action}"
        if request.details:
            action_message += f": {request.details}"
        
        return SuccessResponse(
            message=action_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing flagged content action: {str(e)}"
        )

