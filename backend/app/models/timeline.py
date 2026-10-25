import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class TimelineCategoryEnum(str, enum.Enum):
    CLINICAL = "CLINICAL"
    MEDICATION = "MEDICATION"
    FITNESS = "FITNESS"
    WELLNESS = "WELLNESS"
    APPOINTMENT = "APPOINTMENT"
    REMINDER = "REMINDER"
    GENERAL = "GENERAL"

class TimelineEventTypeEnum(str, enum.Enum):
    METRIC_LOGGED = "METRIC_LOGGED"
    REPORT_UPLOADED = "REPORT_UPLOADED"
    REPORT_CONFIRMED = "REPORT_CONFIRMED"
    PRESCRIPTION_ADDED = "PRESCRIPTION_ADDED"
    MEDICATION_STARTED = "MEDICATION_STARTED"
    MEDICATION_COMPLETED = "MEDICATION_COMPLETED"
    APPOINTMENT_SCHEDULED = "APPOINTMENT_SCHEDULED"
    REMINDER_COMPLETED = "REMINDER_COMPLETED"
    MOOD_LOGGED = "MOOD_LOGGED"
    GOAL_ACHIEVED = "GOAL_ACHIEVED"
    WORKOUT_COMPLETED = "WORKOUT_COMPLETED"
    FITNESS_MILESTONE = "FITNESS_MILESTONE"
    CUSTOM_MILESTONE = "CUSTOM_MILESTONE"
    SYSTEM_NOTICE = "SYSTEM_NOTICE"

class HealthTimelineEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "health_timeline_events"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category: Mapped[TimelineCategoryEnum] = mapped_column(Enum(TimelineCategoryEnum, name="timeline_category_enum", native_enum=False), default=TimelineCategoryEnum.GENERAL, nullable=False, index=True)
    event_type: Mapped[TimelineEventTypeEnum] = mapped_column(Enum(TimelineEventTypeEnum, name="timeline_event_type_enum", native_enum=False), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    reference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True) # e.g. document_id, metric_id, appointment_id
    reference_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # e.g. "health_metric", "medical_report"
    metadata_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="timeline_events")
