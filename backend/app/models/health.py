import enum
import uuid
from datetime import datetime, date, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, Boolean, Date, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class MetricTypeEnum(str, enum.Enum):
    # Vitals
    BLOOD_PRESSURE_SYSTOLIC = "BLOOD_PRESSURE_SYSTOLIC"
    BLOOD_PRESSURE_DIASTOLIC = "BLOOD_PRESSURE_DIASTOLIC"
    HEART_RATE = "HEART_RATE"
    OXYGEN_SATURATION = "OXYGEN_SATURATION"
    BODY_TEMPERATURE = "BODY_TEMPERATURE"
    
    # Body Measurements
    WEIGHT = "WEIGHT"
    HEIGHT = "HEIGHT"
    BMI = "BMI"
    
    # Lab & Blood Test Vitals
    BLOOD_GLUCOSE_FASTING = "BLOOD_GLUCOSE_FASTING"
    BLOOD_GLUCOSE_POSTPRANDIAL = "BLOOD_GLUCOSE_POSTPRANDIAL"
    BLOOD_GLUCOSE_RANDOM = "BLOOD_GLUCOSE_RANDOM"
    HBA1C = "HBA1C"
    HEMOGLOBIN = "HEMOGLOBIN"
    CHOLESTEROL_TOTAL = "CHOLESTEROL_TOTAL"
    CHOLESTEROL_HDL = "CHOLESTEROL_HDL"
    CHOLESTEROL_LDL = "CHOLESTEROL_LDL"
    TRIGLYCERIDES = "TRIGLYCERIDES"
    TSH = "TSH"

class MetricSourceEnum(str, enum.Enum):
    MANUAL = "MANUAL"
    OCR_EXTRACTION = "OCR_EXTRACTION"
    WEARABLE = "WEARABLE"
    SYSTEM_CALCULATED = "SYSTEM_CALCULATED"

class AllergySeverityEnum(str, enum.Enum):
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    LIFE_THREATENING = "LIFE_THREATENING"

class ConditionStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    MANAGED = "MANAGED"
    RESOLVED = "RESOLVED"

class GoalStatusEnum(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    ACHIEVED = "ACHIEVED"
    ABANDONED = "ABANDONED"

class HealthMetric(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "health_metrics"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_type: Mapped[MetricTypeEnum] = mapped_column(Enum(MetricTypeEnum, name="metric_type_enum", native_enum=False), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    source: Mapped[MetricSourceEnum] = mapped_column(Enum(MetricSourceEnum, name="metric_source_enum", native_enum=False), default=MetricSourceEnum.MANUAL, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    metadata_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="metrics")

class Allergy(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "allergies"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    allergen: Mapped[str] = mapped_column(String(150), nullable=False)
    reaction: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    severity: Mapped[AllergySeverityEnum] = mapped_column(Enum(AllergySeverityEnum, name="allergy_severity_enum", native_enum=False), default=AllergySeverityEnum.MODERATE, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="allergies")

class MedicalCondition(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "medical_conditions"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    condition_name: Mapped[str] = mapped_column(String(150), nullable=False)
    diagnosed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[ConditionStatusEnum] = mapped_column(Enum(ConditionStatusEnum, name="condition_status_enum", native_enum=False), default=ConditionStatusEnum.ACTIVE, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="conditions")

class HealthGoal(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "health_goals"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    goal_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., "WEIGHT_LOSS", "STEPS_DAILY", "BLOOD_SUGAR_CONTROL"
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    current_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[GoalStatusEnum] = mapped_column(Enum(GoalStatusEnum, name="goal_status_enum", native_enum=False), default=GoalStatusEnum.IN_PROGRESS, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="goals")

class LifestyleProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "lifestyle_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    diet_type: Mapped[str] = mapped_column(String(100), default="OMNIVORE", nullable=False) # e.g. VEGETARIAN, VEGAN, OMNIVORE, KETO
    activity_level: Mapped[str] = mapped_column(String(100), default="MODERATE", nullable=False) # SEDENTARY, LIGHT, MODERATE, VERY_ACTIVE
    smoking_status: Mapped[str] = mapped_column(String(50), default="NON_SMOKER", nullable=False)
    alcohol_status: Mapped[str] = mapped_column(String(50), default="OCCASIONAL", nullable=False)
    sleep_target_hours: Mapped[float] = mapped_column(Float, default=8.0, nullable=False)
    water_target_liters: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="lifestyle")
