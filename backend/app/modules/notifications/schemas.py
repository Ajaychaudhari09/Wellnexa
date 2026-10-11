import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.notification import NotificationTypeEnum, NotificationPriorityEnum

class SendNotificationRequest(BaseModel):
    notification_type: NotificationTypeEnum = NotificationTypeEnum.SYSTEM_NOTICE
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)
    priority: NotificationPriorityEnum = NotificationPriorityEnum.NORMAL
    action_url: Optional[str] = None
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None

class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    notification_type: str
    title: str
    body: str
    is_read: bool
    action_url: Optional[str] = None
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None
    priority: str
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationUnreadCountResponse(BaseModel):
    unread_count: int
