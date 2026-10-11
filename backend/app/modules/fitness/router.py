import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.modules.fitness.schemas import (
    WorkoutCreateRequest,
    WorkoutResponse,
    DailyActivityLogRequest,
    DailyActivityResponse,
    HabitCreateRequest,
    HabitResponse,
    HabitCheckInRequest,
    HabitCheckInResponse,
    FitnessTrendsResponse,
)
from app.modules.fitness.service import FitnessService

router = APIRouter(prefix="/fitness", tags=["Fitness & Lifestyle Tracking"])

@router.post("/workouts", response_model=ApiResponse[WorkoutResponse], status_code=status.HTTP_201_CREATED)
async def log_workout(
    req: WorkoutCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[WorkoutResponse]:
    """Log a workout session, updating daily active minutes and timeline events."""
    service = FitnessService(db)
    workout = await service.log_workout(current_user.id, req)
    payload = WorkoutResponse.model_validate(workout)
    return ApiResponse[WorkoutResponse](success=True, message="Workout logged successfully", data=payload)

@router.get("/workouts", response_model=ApiResponse[List[WorkoutResponse]], status_code=status.HTTP_200_OK)
async def get_workouts(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[WorkoutResponse]]:
    """Retrieve logged workout sessions."""
    service = FitnessService(db)
    workouts = await service.get_workouts(current_user.id, limit=limit)
    payload = [WorkoutResponse.model_validate(w) for w in workouts]
    return ApiResponse[List[WorkoutResponse]](success=True, message="Workouts retrieved", data=payload)

@router.post("/daily-activity", response_model=ApiResponse[DailyActivityResponse], status_code=status.HTTP_200_OK)
async def log_daily_activity(
    req: DailyActivityLogRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DailyActivityResponse]:
    """Log or update daily lifestyle metrics (steps, sleep hours/quality, water intake, stress level)."""
    service = FitnessService(db)
    summary = await service.log_daily_activity(current_user.id, req)
    payload = DailyActivityResponse.model_validate(summary)
    return ApiResponse[DailyActivityResponse](success=True, message="Daily activity updated", data=payload)

@router.get("/daily-activity", response_model=ApiResponse[DailyActivityResponse], status_code=status.HTTP_200_OK)
async def get_daily_activity(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DailyActivityResponse]:
    """Get today's aggregated activity and lifestyle metrics."""
    service = FitnessService(db)
    summary = await service.get_daily_activity(current_user.id)
    payload = DailyActivityResponse.model_validate(summary)
    return ApiResponse[DailyActivityResponse](success=True, message="Daily activity retrieved", data=payload)

@router.get("/trends", response_model=ApiResponse[FitnessTrendsResponse], status_code=status.HTTP_200_OK)
async def get_fitness_trends(
    days: int = Query(7, ge=3, le=90),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FitnessTrendsResponse]:
    """Retrieve weekly trends and averages for steps, active calories, sleep, and water intake."""
    service = FitnessService(db)
    trends = await service.get_fitness_trends(current_user.id, days=days)
    return ApiResponse[FitnessTrendsResponse](success=True, message="Fitness trends retrieved", data=trends)

@router.post("/habits", response_model=ApiResponse[HabitResponse], status_code=status.HTTP_201_CREATED)
async def create_habit(
    req: HabitCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[HabitResponse]:
    """Create a new daily or weekly health habit."""
    service = FitnessService(db)
    habit = await service.create_habit(current_user.id, req)
    payload = HabitResponse.model_validate(habit)
    return ApiResponse[HabitResponse](success=True, message="Habit created", data=payload)

@router.get("/habits", response_model=ApiResponse[List[HabitResponse]], status_code=status.HTTP_200_OK)
async def get_habits(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[HabitResponse]]:
    """List active habits with today's completion status and current streaks."""
    service = FitnessService(db)
    habits = await service.get_user_habits(current_user.id)
    return ApiResponse[List[HabitResponse]](success=True, message="Habits retrieved", data=habits)

@router.post("/habits/{habit_id}/check-in", response_model=ApiResponse[HabitCheckInResponse], status_code=status.HTTP_200_OK)
async def check_in_habit(
    habit_id: uuid.UUID,
    req: HabitCheckInRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[HabitCheckInResponse]:
    """Check in habit completion for today, advancing current and longest streaks."""
    service = FitnessService(db)
    res = await service.check_in_habit(current_user.id, habit_id, req)
    return ApiResponse[HabitCheckInResponse](success=True, message=res.message, data=res)
