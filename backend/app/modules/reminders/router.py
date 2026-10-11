import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.models.reminder import ReminderTypeEnum
from app.modules.reminders.schemas import (
    ReminderCreateRequest,
    ReminderUpdateRequest,
    ReminderResponse,
    ReminderActionRequest,
    ReminderLogResponse,
    TodayUpcomingRemindersResponse,
    NotificationPreferenceUpdateRequest,
    NotificationPreferenceResponse,
)
from app.modules.reminders.service import ReminderService

router = APIRouter(prefix="/reminders", tags=["Central Smart Reminder Engine"])

@router.post("", response_model=ApiResponse[ReminderResponse], status_code=status.HTTP_201_CREATED)
async def create_reminder(
    req: ReminderCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ReminderResponse]:
    """Create a new smart reminder with recurrence and timeline registration."""
    service = ReminderService(db)
    rem = await service.create_reminder(current_user.id, req)
    payload = ReminderResponse.model_validate(rem)
    return ApiResponse[ReminderResponse](success=True, message="Reminder created", data=payload)

@router.get("", response_model=ApiResponse[List[ReminderResponse]], status_code=status.HTTP_200_OK)
async def get_reminders(
    reminder_type: Optional[ReminderTypeEnum] = Query(None, description="Filter by reminder type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[ReminderResponse]]:
    """List all reminders configured by the user."""
    service = ReminderService(db)
    rems = await service.get_user_reminders(current_user.id, reminder_type=reminder_type, is_active=is_active)
    payload = [ReminderResponse.model_validate(r) for r in rems]
    return ApiResponse[List[ReminderResponse]](success=True, message="Reminders retrieved", data=payload)

@router.get("/today", response_model=ApiResponse[TodayUpcomingRemindersResponse], status_code=status.HTTP_200_OK)
async def get_today_reminders(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TodayUpcomingRemindersResponse]:
    """Get today's due and completed reminders across all categories for dashboard widgets."""
    service = ReminderService(db)
    today_data = await service.get_today_due_reminders(current_user.id)
    return ApiResponse[TodayUpcomingRemindersResponse](success=True, message="Today's reminders retrieved", data=today_data)

@router.post("/{reminder_id}/action", response_model=ApiResponse[ReminderLogResponse], status_code=status.HTTP_200_OK)
async def action_reminder(
    reminder_id: uuid.UUID,
    req: ReminderActionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ReminderLogResponse]:
    """Mark reminder as COMPLETED, SNOOZED, or DISMISSED, recording event in health timeline."""
    service = ReminderService(db)
    log = await service.action_reminder(current_user.id, reminder_id, req)
    payload = ReminderLogResponse.model_validate(log)
    return ApiResponse[ReminderLogResponse](success=True, message=f"Reminder marked as {req.status.value}", data=payload)

@router.patch("/{reminder_id}", response_model=ApiResponse[ReminderResponse], status_code=status.HTTP_200_OK)
async def update_reminder(
    reminder_id: uuid.UUID,
    req: ReminderUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ReminderResponse]:
    """Update reminder title, time, or recurrence schedule."""
    service = ReminderService(db)
    rem = await service.update_reminder(current_user.id, reminder_id, req)
    payload = ReminderResponse.model_validate(rem)
    return ApiResponse[ReminderResponse](success=True, message="Reminder updated", data=payload)

@router.delete("/{reminder_id}", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def delete_reminder(
    reminder_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    """Delete a reminder."""
    service = ReminderService(db)
    await service.delete_reminder(current_user.id, reminder_id)
    return ApiResponse[dict](success=True, message="Reminder deleted", data={"id": str(reminder_id)})

# ----------------- Preferences -----------------
@router.get("/preferences", response_model=ApiResponse[NotificationPreferenceResponse], status_code=status.HTTP_200_OK)
async def get_preferences(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[NotificationPreferenceResponse]:
    """Get user notification preferences."""
    service = ReminderService(db)
    pref = await service.get_or_create_preferences(current_user.id)
    payload = NotificationPreferenceResponse.model_validate(pref)
    return ApiResponse[NotificationPreferenceResponse](success=True, message="Preferences retrieved", data=payload)

@router.put("/preferences", response_model=ApiResponse[NotificationPreferenceResponse], status_code=status.HTTP_200_OK)
async def update_preferences(
    req: NotificationPreferenceUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[NotificationPreferenceResponse]:
    """Update notification preferences and quiet hours."""
    service = ReminderService(db)
    pref = await service.update_preferences(current_user.id, req)
    payload = NotificationPreferenceResponse.model_validate(pref)
    return ApiResponse[NotificationPreferenceResponse](success=True, message="Preferences updated", data=payload)
