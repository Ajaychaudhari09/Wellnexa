import enum
import uuid
from datetime import datetime, date, timezone
from typing import Optional
from sqlalchemy import String, Boolean, Date, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class AppointmentStatusEnum(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class AppointmentTypeEnum(str, enum.Enum):
    IN_PERSON = "IN_PERSON"
    TELEHEALTH = "TELEHEALTH"
    FOLLOW_UP = "FOLLOW_UP"

class Appointment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "appointments"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    doctor_name: Mapped[str] = mapped_column(String(150), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), default="General Medicine", nullable=False)
    clinic_or_hospital: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    appointment_time: Mapped[str] = mapped_column(String(20), default="10:00", nullable=False)
    purpose: Mapped[str] = mapped_column(String(300), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[AppointmentStatusEnum] = mapped_column(
        Enum(AppointmentStatusEnum, name="appointment_status_enum", native_enum=False),
        default=AppointmentStatusEnum.SCHEDULED,
        nullable=False,
        index=True
    )
    appointment_type: Mapped[AppointmentTypeEnum] = mapped_column(
        Enum(AppointmentTypeEnum, name="appointment_type_enum", native_enum=False),
        default=AppointmentTypeEnum.IN_PERSON,
        nullable=False
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    doctor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[doctor_id])
