import enum
import uuid
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Float, Boolean, Date, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin
from app.models.health import MetricTypeEnum

class ReportTypeEnum(str, enum.Enum):
    CBC = "CBC"
    BLOOD_GLUCOSE = "BLOOD_GLUCOSE"
    LIPID_PROFILE = "LIPID_PROFILE"
    THYROID_PROFILE = "THYROID_PROFILE"
    GENERAL_LAB_REPORT = "GENERAL_LAB_REPORT"

class ExtractionStatusEnum(str, enum.Enum):
    PENDING_OCR = "PENDING_OCR"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"

class FlagStatusEnum(str, enum.Enum):
    NORMAL = "NORMAL"
    LOW = "LOW"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"

class MedicalReport(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "medical_reports"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("medical_documents.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    report_type: Mapped[ReportTypeEnum] = mapped_column(Enum(ReportTypeEnum, name="report_type_enum", native_enum=False), default=ReportTypeEnum.GENERAL_LAB_REPORT, nullable=False, index=True)
    report_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    lab_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    status: Mapped[ExtractionStatusEnum] = mapped_column(Enum(ExtractionStatusEnum, name="extraction_status_enum", native_enum=False), default=ExtractionStatusEnum.PENDING_CONFIRMATION, nullable=False, index=True)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary_notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    metadata_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="reports")
    document: Mapped["MedicalDocument"] = relationship("MedicalDocument", back_populates="report")
    extractions: Mapped[List["ReportExtractionItem"]] = relationship("ReportExtractionItem", back_populates="report", cascade="all, delete-orphan", lazy="selectin")

class ReportExtractionItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "report_extractions"

    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("medical_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    test_name: Mapped[str] = mapped_column(String(150), nullable=False)
    metric_type: Mapped[Optional[MetricTypeEnum]] = mapped_column(Enum(MetricTypeEnum, name="metric_type_enum", native_enum=False), nullable=True, index=True)
    detected_value: Mapped[float] = mapped_column(Float, nullable=False)
    confirmed_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_range_low: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reference_range_high: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    flag_status: Mapped[FlagStatusEnum] = mapped_column(Enum(FlagStatusEnum, name="flag_status_enum", native_enum=False), default=FlagStatusEnum.NORMAL, nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_corrected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    report: Mapped["MedicalReport"] = relationship("MedicalReport", back_populates="extractions")
