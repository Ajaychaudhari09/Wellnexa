import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, Integer, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class UserConsent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_consents"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    allow_ai_analysis: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_anonymized_insights: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_doctor_sharing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_retention_days: Mapped[int] = mapped_column(Integer, default=365, nullable=False) # e.g. 365 days / 0 for forever

    user: Mapped["User"] = relationship("User", back_populates="consent")

class AccessAuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "access_audit_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    actor_role: Mapped[str] = mapped_column(String(50), default="PATIENT", nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # e.g. "EXPORT_DATA", "DOCTOR_VIEW", "REPORT_VIEW"
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="access_audit_logs")
