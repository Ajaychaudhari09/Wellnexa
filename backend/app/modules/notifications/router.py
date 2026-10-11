import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.modules.notifications.schemas import (
    NotificationResponse,
    NotificationUnreadCountResponse,
    SendNotificationRequest,
)
from app.modules.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notification Center"])

@router.get("", response_model=ApiResponse[List[NotificationResponse]], status_code=status.HTTP_200_OK)
async def list_notifications(
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[NotificationResponse]]:
    """List all notifications in the In-App Notification Center."""
    service = NotificationService(db)
    notifs = await service.get_user_notifications(current_user.id, is_read=is_read, limit=limit, offset=offset)
    payload = [NotificationResponse.model_validate(n) for n in notifs]
    return ApiResponse[List[NotificationResponse]](success=True, message="Notifications retrieved", data=payload)

@router.get("/unread-count", response_model=ApiResponse[NotificationUnreadCountResponse], status_code=status.HTTP_200_OK)
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[NotificationUnreadCountResponse]:
    """Get the unread badge count for top navigation bar."""
    service = NotificationService(db)
    count = await service.get_unread_count(current_user.id)
    return ApiResponse[NotificationUnreadCountResponse](
        success=True,
        message="Unread count retrieved",
        data=NotificationUnreadCountResponse(unread_count=count),
    )

@router.post("/{notification_id}/read", response_model=ApiResponse[NotificationResponse], status_code=status.HTTP_200_OK)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[NotificationResponse]:
    """Mark a single notification as read."""
    service = NotificationService(db)
    notif = await service.mark_as_read(current_user.id, notification_id)
    payload = NotificationResponse.model_validate(notif)
    return ApiResponse[NotificationResponse](success=True, message="Notification marked as read", data=payload)

@router.post("/mark-all-read", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    """Mark all unread notifications as read."""
    service = NotificationService(db)
    count = await service.mark_all_as_read(current_user.id)
    return ApiResponse[dict](success=True, message="All notifications marked as read", data={"updated_count": count})

@router.post("/test-dispatch", response_model=ApiResponse[NotificationResponse], status_code=status.HTTP_201_CREATED)
async def test_dispatch_notification(
    req: SendNotificationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[NotificationResponse]:
    """Test notification dispatch across in-app, push, and email channels."""
    service = NotificationService(db)
    notif = await service.dispatch_notification(current_user.id, req)
    payload = NotificationResponse.model_validate(notif)
    return ApiResponse[NotificationResponse](success=True, message="Notification dispatched", data=payload)
