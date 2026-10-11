import enum
import uuid
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, Date, DateTime, Enum, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class AccessScopeEnum(str, enum.Enum):
    FULL_ACCESS = "FULL_ACCESS"
    REPORTS_ONLY = "REPORTS_ONLY"
    MEDICATIONS_ONLY = "MEDICATIONS_ONLY"
    VITALS_ONLY = "VITALS_ONLY"

class GrantStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

class PatientAccessGrant(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "patient_access_grants"

    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    access_token: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    access_scope: Mapped[AccessScopeEnum] = mapped_column(Enum(AccessScopeEnum, name="access_scope_enum", native_enum=False), default=AccessScopeEnum.FULL_ACCESS, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[GrantStatusEnum] = mapped_column(Enum(GrantStatusEnum, name="grant_status_enum", native_enum=False), default=GrantStatusEnum.ACTIVE, nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    patient: Mapped["User"] = relationship("User", foreign_keys=[patient_id], back_populates="patient_grants")
    doctor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_grants")

class DoctorConsultation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "doctor_consultations"

    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    doctor_name: Mapped[str] = mapped_column(String(150), nullable=False)
    clinic_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    consultation_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False, index=True)
    chief_complaint: Mapped[str] = mapped_column(String(300), nullable=False)
    clinical_observations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_actions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    patient: Mapped["User"] = relationship("User", foreign_keys=[patient_id], back_populates="patient_consultations")
    doctor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_consultations")
