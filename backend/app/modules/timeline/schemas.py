import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.timeline import TimelineCategoryEnum, TimelineEventTypeEnum

class TimelineCustomEventRequest(BaseModel):
    category: TimelineCategoryEnum = TimelineCategoryEnum.GENERAL
    title: str = Field(..., min_length=1, max_length=200)
    summary: Optional[str] = Field(None, max_length=500)
    occurred_at: Optional[datetime] = None
    metadata_info: Optional[Dict[str, Any]] = None

class PinEventRequest(BaseModel):
    is_pinned: bool

class TimelineEventResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    category: str
    event_type: str
    title: str
    summary: Optional[str] = None
    occurred_at: datetime
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None
    metadata_info: Optional[Dict[str, Any]] = None
    is_pinned: bool

    class Config:
        from_attributes = True

class TimelineFeedResponse(BaseModel):
    events: List[TimelineEventResponse]
    total_count: int
    has_more: bool
