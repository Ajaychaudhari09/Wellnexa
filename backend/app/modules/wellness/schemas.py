import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.wellness import EmotionEnum

class MoodLogCreateRequest(BaseModel):
    mood_score: int = Field(..., ge=1, le=5, description="1 (Very Low) to 5 (Great)")
    primary_emotion: EmotionEnum = EmotionEnum.CONTENT
    tags: Optional[List[str]] = []
    journal_text: Optional[str] = None
    gratitude_note: Optional[str] = Field(None, max_length=500)
    sleep_quality: Optional[int] = Field(3, ge=1, le=5)
    logged_date: Optional[date] = None

class CrisisSupportInfo(BaseModel):
    support_message: str
    helpline_resources: Dict[str, Any]

class MoodLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    mood_score: int
    primary_emotion: str
    tags: List[str] = []
    journal_text: Optional[str] = None
    gratitude_note: Optional[str] = None
    sleep_quality: Optional[int] = None
    logged_date: date
    crisis_flag: bool
    is_crisis_detected: bool = False
    crisis_support: Optional[CrisisSupportInfo] = None
    crisis_resources: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class WeeklyMoodTrendItem(BaseModel):
    date: date
    day_name: str
    mood_score: Optional[int] = None
    primary_emotion: Optional[str] = None
    sleep_quality: Optional[int] = None

class WeeklyMoodTrendsResponse(BaseModel):
    average_mood_score: float
    predominant_emotion: str
    total_entries_this_week: int
    trends: List[WeeklyMoodTrendItem]
