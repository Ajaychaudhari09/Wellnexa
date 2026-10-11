import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.reminder import ReminderTypeEnum, RecurrenceTypeEnum, ReminderStatusEnum

class ReminderCreateRequest(BaseModel):
    reminder_type: ReminderTypeEnum = ReminderTypeEnum.CUSTOM
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    recurrence: RecurrenceTypeEnum = RecurrenceTypeEnum.ONCE
    due_date: Optional[date] = None
    due_time: str = Field(default="09:00", description="Time in HH:MM format")
    days_of_week: Optional[str] = "DAILY"
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None
    metadata_info: Optional[Dict[str, Any]] = None

class ReminderUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    recurrence: Optional[RecurrenceTypeEnum] = None
    due_date: Optional[date] = None
    due_time: Optional[str] = None
    days_of_week: Optional[str] = None
    is_active: Optional[bool] = None

class ReminderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    reminder_type: str
    title: str
    description: Optional[str] = None
    recurrence: str
    due_date: Optional[date] = None
    due_time: str
    days_of_week: Optional[str] = None
    is_active: bool
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None
    metadata_info: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReminderActionRequest(BaseModel):
    status: ReminderStatusEnum = ReminderStatusEnum.COMPLETED # COMPLETED, SNOOZED, DISMISSED
    notes: Optional[str] = None

class ReminderLogResponse(BaseModel):
    id: uuid.UUID
    reminder_id: uuid.UUID
    user_id: uuid.UUID
    scheduled_at: datetime
    status: str
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class DueReminderItem(BaseModel):
    reminder_id: uuid.UUID
    reminder_type: str
    title: str
    description: Optional[str] = None
    due_time: str
    recurrence: str
    status: str # PENDING, COMPLETED, SNOOZED
    log_id: Optional[uuid.UUID] = None

class TodayUpcomingRemindersResponse(BaseModel):
    date: date
    total_due: int
    completed_count: int
    pending_count: int
    reminders: List[DueReminderItem]

class NotificationPreferenceUpdateRequest(BaseModel):
    enable_in_app: Optional[bool] = None
    enable_email: Optional[bool] = None
    enable_push: Optional[bool] = None
    medicine_alerts: Optional[bool] = None
    refill_alerts: Optional[bool] = None
    appointment_alerts: Optional[bool] = None
    wellness_nudges: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None

class NotificationPreferenceResponse(BaseModel):
    user_id: uuid.UUID
    enable_in_app: bool
    enable_email: bool
    enable_push: bool
    medicine_alerts: bool
    refill_alerts: bool
    appointment_alerts: bool
    wellness_nudges: bool
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None

    class Config:
        from_attributes = True
