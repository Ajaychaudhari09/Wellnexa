import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class NotificationTypeEnum(str, enum.Enum):
    MEDICINE_DUE = "MEDICINE_DUE"
    REFILL_ALERT = "REFILL_ALERT"
    APPOINTMENT_UPCOMING = "APPOINTMENT_UPCOMING"
    REPORT_CRITICAL = "REPORT_CRITICAL"
    WEEKLY_ADHERENCE = "WEEKLY_ADHERENCE"
    SYSTEM_NOTICE = "SYSTEM_NOTICE"
    SECURITY_ALERT = "SECURITY_ALERT"

class NotificationPriorityEnum(str, enum.Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"

class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    notification_type: Mapped[NotificationTypeEnum] = mapped_column(Enum(NotificationTypeEnum, name="notification_type_enum", native_enum=False), default=NotificationTypeEnum.SYSTEM_NOTICE, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    action_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reference_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    priority: Mapped[NotificationPriorityEnum] = mapped_column(Enum(NotificationPriorityEnum, name="notification_priority_enum", native_enum=False), default=NotificationPriorityEnum.NORMAL, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="notifications")
