import enum
import uuid
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Float, Integer, Boolean, Date, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class MedicationFormEnum(str, enum.Enum):
    TABLET = "TABLET"
    CAPSULE = "CAPSULE"
    SYRUP = "SYRUP"
    INJECTION = "INJECTION"
    DROPS = "DROPS"
    INHALER = "INHALER"
    CREAM = "CREAM"
    OTHER = "OTHER"

class FrequencyEnum(str, enum.Enum):
    ONCE_DAILY = "ONCE_DAILY"
    TWICE_DAILY = "TWICE_DAILY"
    THRICE_DAILY = "THRICE_DAILY"
    FOUR_TIMES_DAILY = "FOUR_TIMES_DAILY"
    AS_NEEDED = "AS_NEEDED"
    CUSTOM = "CUSTOM"

class TimingEnum(str, enum.Enum):
    BEFORE_MEAL = "BEFORE_MEAL"
    AFTER_MEAL = "AFTER_MEAL"
    WITH_MEAL = "WITH_MEAL"
    EMPTY_STOMACH = "EMPTY_STOMACH"
    BEDTIME = "BEDTIME"
    ANYTIME = "ANYTIME"

class DoseStatusEnum(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    TAKEN = "TAKEN"
    MISSED = "MISSED"
    SKIPPED = "SKIPPED"

class Prescription(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "prescriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("medical_documents.id", ondelete="SET NULL"), nullable=True, index=True)
    doctor_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    clinic_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    prescribed_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False)
    diagnosis_notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="prescriptions")
    medications: Mapped[List["Medication"]] = relationship("Medication", back_populates="prescription", cascade="all, delete-orphan", lazy="selectin")

class Medication(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "medications"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    prescription_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("prescriptions.id", ondelete="SET NULL"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    dosage: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "500 mg", "10 ml"
    form: Mapped[MedicationFormEnum] = mapped_column(Enum(MedicationFormEnum, name="medication_form_enum", native_enum=False), default=MedicationFormEnum.TABLET, nullable=False)
    frequency: Mapped[FrequencyEnum] = mapped_column(Enum(FrequencyEnum, name="frequency_enum", native_enum=False), default=FrequencyEnum.ONCE_DAILY, nullable=False)
    timing: Mapped[TimingEnum] = mapped_column(Enum(TimingEnum, name="timing_enum", native_enum=False), default=TimingEnum.AFTER_MEAL, nullable=False)
    instructions: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    current_stock: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    refill_threshold: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    user: Mapped["User"] = relationship("User", back_populates="medications")
    prescription: Mapped[Optional["Prescription"]] = relationship("Prescription", back_populates="medications")
    schedules: Mapped[List["MedicationSchedule"]] = relationship("MedicationSchedule", back_populates="medication", cascade="all, delete-orphan", lazy="selectin")
    logs: Mapped[List["MedicationLog"]] = relationship("MedicationLog", back_populates="medication", cascade="all, delete-orphan")

class MedicationSchedule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "medication_schedules"

    medication_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("medications.id", ondelete="CASCADE"), nullable=False, index=True)
    time_slot: Mapped[str] = mapped_column(String(10), nullable=False) # e.g. "09:00", "21:00"
    dosage_quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    days_of_week: Mapped[Optional[str]] = mapped_column(String(50), default="DAILY", nullable=False) # e.g. "DAILY", "MON,WED,FRI"

    medication: Mapped["Medication"] = relationship("Medication", back_populates="schedules")

class MedicationLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "medication_logs"

    medication_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("medications.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[DoseStatusEnum] = mapped_column(Enum(DoseStatusEnum, name="dose_status_enum", native_enum=False), default=DoseStatusEnum.SCHEDULED, nullable=False, index=True)
    taken_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    medication: Mapped["Medication"] = relationship("Medication", back_populates="logs")
    user: Mapped["User"] = relationship("User", back_populates="medication_logs")
