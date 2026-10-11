import enum
import uuid
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Float, Integer, Boolean, Date, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class ActivityTypeEnum(str, enum.Enum):
    RUNNING = "RUNNING"
    WALKING = "WALKING"
    CYCLING = "CYCLING"
    SWIMMING = "SWIMMING"
    STRENGTH_TRAINING = "STRENGTH_TRAINING"
    YOGA = "YOGA"
    HIIT = "HIIT"
    PILATES = "PILATES"
    SPORTS = "SPORTS"
    CUSTOM = "CUSTOM"

class WorkoutIntensityEnum(str, enum.Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VIGOROUS = "VIGOROUS"

class WorkoutLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workout_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_type: Mapped[ActivityTypeEnum] = mapped_column(Enum(ActivityTypeEnum, name="activity_type_enum", native_enum=False), default=ActivityTypeEnum.CUSTOM, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    calories_burned: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    intensity: Mapped[WorkoutIntensityEnum] = mapped_column(Enum(WorkoutIntensityEnum, name="workout_intensity_enum", native_enum=False), default=WorkoutIntensityEnum.MODERATE, nullable=False)
    distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    heart_rate_avg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    logged_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="workouts")

class DailyActivitySummary(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "daily_activity_summaries"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False, index=True)
    steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    calories_burned: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    water_ml: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sleep_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sleep_quality: Mapped[Optional[int]] = mapped_column(Integer, default=3, nullable=True) # 1 to 5
    stress_level: Mapped[Optional[int]] = mapped_column(Integer, default=5, nullable=True) # 1 to 10

    user: Mapped["User"] = relationship("User", back_populates="daily_activities")

class Habit(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "habits"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), default="General", nullable=False)
    frequency: Mapped[str] = mapped_column(String(50), default="DAILY", nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    user: Mapped["User"] = relationship("User", back_populates="habits")
    logs: Mapped[List["HabitLog"]] = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")

class HabitLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "habit_logs"

    habit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("habits.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    logged_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False, index=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    habit: Mapped["Habit"] = relationship("Habit", back_populates="logs")
