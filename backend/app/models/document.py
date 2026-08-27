import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class DocumentCategoryEnum(str, enum.Enum):
    MEDICAL_REPORT = "MEDICAL_REPORT"
    PRESCRIPTION = "PRESCRIPTION"
    LAB_INVOICE = "LAB_INVOICE"
    DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY"
    OTHER = "OTHER"

class DocumentStatusEnum(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING_OCR = "PROCESSING_OCR"
    EXTRACTED = "EXTRACTED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"

class MedicalDocument(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "medical_documents"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category: Mapped[DocumentCategoryEnum] = mapped_column(Enum(DocumentCategoryEnum, name="document_category_enum", native_enum=False), default=DocumentCategoryEnum.MEDICAL_REPORT, nullable=False, index=True)
    status: Mapped[DocumentStatusEnum] = mapped_column(Enum(DocumentStatusEnum, name="document_status_enum", native_enum=False), default=DocumentStatusEnum.UPLOADED, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    metadata_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="documents")
    report: Mapped[Optional["MedicalReport"]] = relationship("MedicalReport", back_populates="document", uselist=False, cascade="all, delete-orphan")
