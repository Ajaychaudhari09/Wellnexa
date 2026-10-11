import uuid
from datetime import datetime, date, timedelta, timezone
from typing import List, Optional, Tuple, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.core.exceptions import NotFoundException, WellNexaException
from app.models.fitness import (
    WorkoutLog,
    DailyActivitySummary,
    Habit,
    HabitLog,
    ActivityTypeEnum,
    WorkoutIntensityEnum,
)
from app.models.timeline import TimelineCategoryEnum, TimelineEventTypeEnum
from app.models.health import HealthMetric, MetricSourceEnum
from app.models.audit import AuditLog
from app.modules.timeline.service import TimelineService
from app.modules.fitness.schemas import (
    WorkoutCreateRequest,
    DailyActivityLogRequest,
    HabitCreateRequest,
    HabitUpdateRequest,
    HabitCheckInRequest,
    HabitCheckInResponse,
    HabitResponse,
    WeeklyActivityTrendItem,
    FitnessTrendsResponse,
)

class FitnessService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.timeline_service = TimelineService(db)

    # ----------------- Workouts -----------------
    async def log_workout(self, user_id: uuid.UUID, req: WorkoutCreateRequest) -> WorkoutLog:
        logged_date = req.logged_date or datetime.now(timezone.utc).date()

        workout = WorkoutLog(
            user_id=user_id,
            activity_type=req.activity_type,
            title=req.title.strip(),
            duration_minutes=req.duration_minutes,
            calories_burned=req.calories_burned,
            intensity=req.intensity,
            distance_km=req.distance_km,
            heart_rate_avg=req.heart_rate_avg,
            logged_date=logged_date,
            notes=req.notes.strip() if req.notes else None,
        )
        self.db.add(workout)
        await self.db.flush()

        # Update Daily Activity Summary
        summary = await self.get_or_create_daily_activity(user_id, logged_date)
        summary.active_minutes += req.duration_minutes
        summary.calories_burned += req.calories_burned
        await self.db.flush()

        # Health Timeline Event
        await self.timeline_service.record_event(
            user_id=user_id,
            category=TimelineCategoryEnum.FITNESS,
            event_type=TimelineEventTypeEnum.WORKOUT_COMPLETED,
            title=f"Workout: {workout.title}",
            summary=f"{workout.duration_minutes} mins • {round(workout.calories_burned, 1)} kcal • {workout.intensity.value.title()}",
            occurred_at=datetime.now(timezone.utc),
            reference_id=str(workout.id),
            reference_type="workout_log",
            metadata_info={"activity": workout.activity_type.value, "duration": workout.duration_minutes},
        )

        return workout

    async def get_workouts(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> List[WorkoutLog]:
        query = select(WorkoutLog).where(WorkoutLog.user_id == user_id).order_by(desc(WorkoutLog.logged_date)).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ----------------- Daily Activity -----------------
    async def get_or_create_daily_activity(self, user_id: uuid.UUID, target_date: date) -> DailyActivitySummary:
        query = select(DailyActivitySummary).where(
            and_(DailyActivitySummary.user_id == user_id, DailyActivitySummary.date == target_date)
        )
        result = await self.db.execute(query)
        summary = result.scalar_one_or_none()
        if not summary:
            summary = DailyActivitySummary(user_id=user_id, date=target_date)
            self.db.add(summary)
            await self.db.flush()
        return summary

    async def log_daily_activity(self, user_id: uuid.UUID, req: DailyActivityLogRequest) -> DailyActivitySummary:
        t_date = req.date or datetime.now(timezone.utc).date()
        summary = await self.get_or_create_daily_activity(user_id, t_date)

        if req.steps is not None:
            summary.steps = req.steps
        if req.active_minutes is not None:
            summary.active_minutes = req.active_minutes
        if req.calories_burned is not None:
            summary.calories_burned = req.calories_burned
        if req.water_ml is not None:
            summary.water_ml = req.water_ml
        if req.sleep_hours is not None:
            summary.sleep_hours = req.sleep_hours
        if req.sleep_quality is not None:
            summary.sleep_quality = req.sleep_quality
        if req.stress_level is not None:
            summary.stress_level = req.stress_level

        await self.db.flush()
        return summary

    async def get_daily_activity(self, user_id: uuid.UUID, target_date: Optional[date] = None) -> DailyActivitySummary:
        t_date = target_date or datetime.now(timezone.utc).date()
        return await self.get_or_create_daily_activity(user_id, t_date)

    # ----------------- Habits -----------------
    async def create_habit(self, user_id: uuid.UUID, req: HabitCreateRequest) -> Habit:
        habit = Habit(
            user_id=user_id,
            title=req.title.strip(),
            description=req.description.strip() if req.description else None,
            category=req.category.strip() if req.category else "General",
            frequency=req.frequency or "DAILY",
            current_streak=0,
            longest_streak=0,
            is_active=True,
        )
        self.db.add(habit)
        await self.db.flush()
        return habit

    async def get_user_habits(self, user_id: uuid.UUID) -> List[HabitResponse]:
        query = select(Habit).where(and_(Habit.user_id == user_id, Habit.is_active == True)).order_by(Habit.created_at.asc())
        result = await self.db.execute(query)
        habits = list(result.scalars().all())

        today = datetime.now(timezone.utc).date()
        response_list: List[HabitResponse] = []

        for h in habits:
            log_q = select(HabitLog).where(
                and_(HabitLog.habit_id == h.id, HabitLog.logged_date == today, HabitLog.is_completed == True)
            )
            log_res = await self.db.execute(log_q)
            is_done = log_res.scalar_one_or_none() is not None

            response_list.append(
                HabitResponse(
                    id=h.id,
                    user_id=h.user_id,
                    title=h.title,
                    description=h.description,
                    category=h.category,
                    frequency=h.frequency,
                    current_streak=h.current_streak,
                    longest_streak=h.longest_streak,
                    is_active=h.is_active,
                    is_completed_today=is_done,
                    created_at=h.created_at,
                )
            )

        return response_list

    async def check_in_habit(self, user_id: uuid.UUID, habit_id: uuid.UUID, req: HabitCheckInRequest) -> HabitCheckInResponse:
        query = select(Habit).where(and_(Habit.id == habit_id, Habit.user_id == user_id))
        result = await self.db.execute(query)
        habit = result.scalar_one_or_none()
        if not habit:
            raise NotFoundException("Habit", habit_id)

        t_date = req.logged_date or datetime.now(timezone.utc).date()

        # Check existing log for this date
        log_q = select(HabitLog).where(and_(HabitLog.habit_id == habit.id, HabitLog.logged_date == t_date))
        log_res = await self.db.execute(log_q)
        h_log = log_res.scalar_one_or_none()

        if not h_log:
            h_log = HabitLog(
                habit_id=habit.id,
                user_id=user_id,
                logged_date=t_date,
                is_completed=req.is_completed,
                notes=req.notes.strip() if req.notes else None,
            )
            self.db.add(h_log)
        else:
            h_log.is_completed = req.is_completed
            if req.notes:
                h_log.notes = req.notes.strip()

        # Update streak
        if req.is_completed:
            habit.current_streak += 1
            if habit.current_streak > habit.longest_streak:
                habit.longest_streak = habit.current_streak

            # Timeline event on streak milestones
            if habit.current_streak in (3, 7, 14, 21, 30, 60, 100):
                await self.timeline_service.record_event(
                    user_id=user_id,
                    category=TimelineCategoryEnum.WELLNESS,
                    event_type=TimelineEventTypeEnum.SYSTEM_NOTICE,
                    title=f"🔥 {habit.current_streak}-Day Streak: {habit.title}",
                    summary=f"Incredible consistency! You've completed {habit.title} for {habit.current_streak} days straight.",
                    occurred_at=datetime.now(timezone.utc),
                    reference_id=str(habit.id),
                    reference_type="habit",
                )

        await self.db.flush()

        return HabitCheckInResponse(
            habit_id=habit.id,
            logged_date=t_date,
            is_completed=req.is_completed,
            current_streak=habit.current_streak,
            longest_streak=habit.longest_streak,
            message=f"Habit check-in saved! Current streak: {habit.current_streak} days.",
        )

    # ----------------- Trends -----------------
    async def get_fitness_trends(self, user_id: uuid.UUID, days: int = 7) -> FitnessTrendsResponse:
        today = datetime.now(timezone.utc).date()
        trend_items: List[WeeklyActivityTrendItem] = []

        for i in range(days - 1, -1, -1):
            d = today - timedelta(days=i)
            q = select(DailyActivitySummary).where(
                and_(DailyActivitySummary.user_id == user_id, DailyActivitySummary.date == d)
            )
            res = await self.db.execute(q)
            summ = res.scalar_one_or_none()

            steps = summ.steps if summ else 0
            mins = summ.active_minutes if summ else 0
            cals = summ.calories_burned if summ else 0.0
            sleep = summ.sleep_hours if summ else 0.0
            water = summ.water_ml if summ else 0
            stress = summ.stress_level if summ else 5

            trend_items.append(
                WeeklyActivityTrendItem(
                    date=d,
                    day_name=d.strftime("%a"),
                    steps=steps,
                    active_minutes=mins,
                    calories_burned=round(cals, 1),
                    sleep_hours=round(sleep, 1),
                    water_ml=water,
                    stress_level=stress,
                )
            )

        avg_steps = int(sum(t.steps for t in trend_items) / float(days))
        avg_mins = int(sum(t.active_minutes for t in trend_items) / float(days))
        avg_cals = round(sum(t.calories_burned for t in trend_items) / float(days), 1)
        avg_sleep = round(sum(t.sleep_hours for t in trend_items) / float(days), 1)
        avg_water = int(sum(t.water_ml for t in trend_items) / float(days))

        return FitnessTrendsResponse(
            average_daily_steps=avg_steps,
            average_active_minutes=avg_mins,
            average_calories_burned=avg_cals,
            average_sleep_hours=avg_sleep,
            average_water_ml=avg_water,
            trends=trend_items,
        )
