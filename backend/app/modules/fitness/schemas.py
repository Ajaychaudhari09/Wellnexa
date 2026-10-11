import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.fitness import ActivityTypeEnum, WorkoutIntensityEnum

# ----------------- Workouts -----------------
class WorkoutCreateRequest(BaseModel):
    activity_type: ActivityTypeEnum = ActivityTypeEnum.CUSTOM
    title: str = Field(..., min_length=1, max_length=150)
    duration_minutes: int = Field(..., gt=0, le=720)
    calories_burned: float = Field(default=0.0, ge=0)
    intensity: WorkoutIntensityEnum = WorkoutIntensityEnum.MODERATE
    distance_km: Optional[float] = Field(None, ge=0)
    heart_rate_avg: Optional[int] = Field(None, ge=30, le=240)
    logged_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=300)

class WorkoutResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    activity_type: str
    title: str
    duration_minutes: int
    calories_burned: float
    intensity: str
    distance_km: Optional[float] = None
    heart_rate_avg: Optional[int] = None
    logged_date: date
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Daily Activity -----------------
class DailyActivityLogRequest(BaseModel):
    date: Optional[date] = None
    steps: Optional[int] = Field(None, ge=0, le=100000)
    active_minutes: Optional[int] = Field(None, ge=0, le=1440)
    calories_burned: Optional[float] = Field(None, ge=0)
    water_ml: Optional[int] = Field(None, ge=0, le=20000)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    sleep_quality: Optional[int] = Field(None, ge=1, le=5)
    stress_level: Optional[int] = Field(None, ge=1, le=10)

class DailyActivityResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    date: date
    steps: int
    active_minutes: int
    calories_burned: float
    water_ml: int
    sleep_hours: float
    sleep_quality: Optional[int] = None
    stress_level: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Habits -----------------
class HabitCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=300)
    category: Optional[str] = "General"
    frequency: Optional[str] = "DAILY"

class HabitUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class HabitResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str] = None
    category: str
    frequency: str
    current_streak: int
    longest_streak: int
    is_active: bool
    is_completed_today: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class HabitCheckInRequest(BaseModel):
    logged_date: Optional[date] = None
    is_completed: bool = True
    notes: Optional[str] = None

class HabitCheckInResponse(BaseModel):
    habit_id: uuid.UUID
    logged_date: date
    is_completed: bool
    current_streak: int
    longest_streak: int
    message: str

# ----------------- Trends -----------------
class WeeklyActivityTrendItem(BaseModel):
    date: date
    day_name: str
    steps: int
    active_minutes: int
    calories_burned: float
    sleep_hours: float
    water_ml: int
    stress_level: Optional[int] = None

class FitnessTrendsResponse(BaseModel):
    average_daily_steps: int
    average_active_minutes: int
    average_calories_burned: float
    average_sleep_hours: float
    average_water_ml: int
    trends: List[WeeklyActivityTrendItem]
