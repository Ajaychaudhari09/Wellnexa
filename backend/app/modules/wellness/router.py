import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.modules.wellness.schemas import (
    MoodLogCreateRequest,
    MoodLogResponse,
    WeeklyMoodTrendsResponse,
)
from app.modules.wellness.service import WellnessService

router = APIRouter(prefix="/wellness", tags=["Mental Wellness & Mood Journal"])

@router.post("/mood", response_model=ApiResponse[MoodLogResponse], status_code=status.HTTP_201_CREATED)
async def log_mood(
    req: MoodLogCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MoodLogResponse]:
    """Log daily mood score, primary emotion, journal reflection, gratitude notes, and perform safety scan."""
    service = WellnessService(db)
    res = await service.log_mood(current_user.id, req)
    return ApiResponse[MoodLogResponse](success=True, message="Mood and journal entry saved successfully", data=res)

@router.get("/mood", response_model=ApiResponse[List[MoodLogResponse]], status_code=status.HTTP_200_OK)
async def get_mood_logs(
    limit: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[MoodLogResponse]]:
    """Retrieve historical mood and journal logs."""
    service = WellnessService(db)
    logs = await service.get_mood_logs(current_user.id, limit=limit)
    payload = [MoodLogResponse.model_validate(m) for m in logs]
    return ApiResponse[List[MoodLogResponse]](success=True, message="Mood logs retrieved", data=payload)

@router.get("/mood/today", response_model=ApiResponse[Optional[MoodLogResponse]], status_code=status.HTTP_200_OK)
async def get_today_mood(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[Optional[MoodLogResponse]]:
    """Check if mood was logged for today."""
    service = WellnessService(db)
    m = await service.get_today_mood(current_user.id)
    payload = MoodLogResponse.model_validate(m) if m else None
    return ApiResponse[Optional[MoodLogResponse]](success=True, message="Today's mood status", data=payload)

@router.get("/mood/trends", response_model=ApiResponse[WeeklyMoodTrendsResponse], status_code=status.HTTP_200_OK)
async def get_mood_trends(
    days: int = Query(7, ge=3, le=90),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[WeeklyMoodTrendsResponse]:
    """Retrieve 7-day emotional trends and sleep correlation."""
    service = WellnessService(db)
    trends = await service.get_weekly_mood_trends(current_user.id, days=days)
    return ApiResponse[WeeklyMoodTrendsResponse](success=True, message="Mood trends retrieved", data=trends)
