import enum
import uuid
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, Date, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class ReminderTypeEnum(str, enum.Enum):
    MEDICINE = "MEDICINE"
    APPOINTMENT = "APPOINTMENT"
    LAB_TEST = "LAB_TEST"
    CHECKUP = "CHECKUP"
    REFILL = "REFILL"
    VACCINATION = "VACCINATION"
    WATER = "WATER"
    EXERCISE = "EXERCISE"
    WELLNESS = "WELLNESS"
    CUSTOM = "CUSTOM"

class RecurrenceTypeEnum(str, enum.Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    CUSTOM = "CUSTOM"

class ReminderStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    SNOOZED = "SNOOZED"
    MISSED = "MISSED"
    DISMISSED = "DISMISSED"

class Reminder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "reminders"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reminder_type: Mapped[ReminderTypeEnum] = mapped_column(Enum(ReminderTypeEnum, name="reminder_type_enum", native_enum=False), default=ReminderTypeEnum.CUSTOM, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    recurrence: Mapped[RecurrenceTypeEnum] = mapped_column(Enum(RecurrenceTypeEnum, name="recurrence_type_enum", native_enum=False), default=RecurrenceTypeEnum.ONCE, nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True) # for one-time or start
    due_time: Mapped[str] = mapped_column(String(10), default="09:00", nullable=False) # e.g. "09:00"
    days_of_week: Mapped[Optional[str]] = mapped_column(String(50), default="DAILY", nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    reference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    reference_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    metadata_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="reminders")
    logs: Mapped[List["ReminderLog"]] = relationship("ReminderLog", back_populates="reminder", cascade="all, delete-orphan")

class ReminderLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "reminder_logs"

    reminder_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reminders.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[ReminderStatusEnum] = mapped_column(Enum(ReminderStatusEnum, name="reminder_status_enum", native_enum=False), default=ReminderStatusEnum.PENDING, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    reminder: Mapped["Reminder"] = relationship("Reminder", back_populates="logs")

class NotificationPreference(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    enable_in_app: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enable_email: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enable_push: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    medicine_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    refill_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    appointment_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    wellness_nudges: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    quiet_hours_start: Mapped[Optional[str]] = mapped_column(String(10), default="22:00", nullable=True)
    quiet_hours_end: Mapped[Optional[str]] = mapped_column(String(10), default="07:00", nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="notification_preferences")
