import enum
import uuid
from typing import List, Optional, Union
from sqlalchemy import String, Boolean, ForeignKey, Enum, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class RoleEnum(str, enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"

# Association table for User <-> Role (Many-to-Many)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

class Role(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "roles"

    name: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum, name="role_enum", native_enum=False), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    users: Mapped[List["User"]] = relationship("User", secondary=user_roles, back_populates="roles")

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    roles: Mapped[List[Role]] = relationship("Role", secondary=user_roles, back_populates="users", lazy="selectin")
    profile: Mapped[Optional["Profile"]] = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    lifestyle: Mapped[Optional["LifestyleProfile"]] = relationship("LifestyleProfile", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    notification_preferences: Mapped[Optional["NotificationPreference"]] = relationship("NotificationPreference", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    nutrition_targets: Mapped[Optional["NutritionTarget"]] = relationship("NutritionTarget", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    consent: Mapped[Optional["UserConsent"]] = relationship("UserConsent", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    access_audit_logs: Mapped[List["AccessAuditLog"]] = relationship("AccessAuditLog", back_populates="user", cascade="all, delete-orphan")
    metrics: Mapped[List["HealthMetric"]] = relationship("HealthMetric", back_populates="user", cascade="all, delete-orphan")
    allergies: Mapped[List["Allergy"]] = relationship("Allergy", back_populates="user", cascade="all, delete-orphan")
    conditions: Mapped[List["MedicalCondition"]] = relationship("MedicalCondition", back_populates="user", cascade="all, delete-orphan")
    goals: Mapped[List["HealthGoal"]] = relationship("HealthGoal", back_populates="user", cascade="all, delete-orphan")
    timeline_events: Mapped[List["HealthTimelineEvent"]] = relationship("HealthTimelineEvent", back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[List["MedicalDocument"]] = relationship("MedicalDocument", back_populates="user", cascade="all, delete-orphan")
    reports: Mapped[List["MedicalReport"]] = relationship("MedicalReport", back_populates="user", cascade="all, delete-orphan")
    prescriptions: Mapped[List["Prescription"]] = relationship("Prescription", back_populates="user", cascade="all, delete-orphan")
    medications: Mapped[List["Medication"]] = relationship("Medication", back_populates="user", cascade="all, delete-orphan")
    medication_logs: Mapped[List["MedicationLog"]] = relationship("MedicationLog", back_populates="user", cascade="all, delete-orphan")
    reminders: Mapped[List["Reminder"]] = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    meal_logs: Mapped[List["MealLog"]] = relationship("MealLog", back_populates="user", cascade="all, delete-orphan")
    meal_plans: Mapped[List["MealPlan"]] = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")
    grocery_lists: Mapped[List["GroceryList"]] = relationship("GroceryList", back_populates="user", cascade="all, delete-orphan")
    workouts: Mapped[List["WorkoutLog"]] = relationship("WorkoutLog", back_populates="user", cascade="all, delete-orphan")
    daily_activities: Mapped[List["DailyActivitySummary"]] = relationship("DailyActivitySummary", back_populates="user", cascade="all, delete-orphan")
    habits: Mapped[List["Habit"]] = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    mood_logs: Mapped[List["MoodLog"]] = relationship("MoodLog", back_populates="user", cascade="all, delete-orphan")
    chat_sessions: Mapped[List["ChatSession"]] = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    chat_messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    patient_grants: Mapped[List["PatientAccessGrant"]] = relationship("PatientAccessGrant", foreign_keys="PatientAccessGrant.patient_id", back_populates="patient", cascade="all, delete-orphan")
    doctor_grants: Mapped[List["PatientAccessGrant"]] = relationship("PatientAccessGrant", foreign_keys="PatientAccessGrant.doctor_id", back_populates="doctor")
    patient_consultations: Mapped[List["DoctorConsultation"]] = relationship("DoctorConsultation", foreign_keys="DoctorConsultation.patient_id", back_populates="patient", cascade="all, delete-orphan")
    doctor_consultations: Mapped[List["DoctorConsultation"]] = relationship("DoctorConsultation", foreign_keys="DoctorConsultation.doctor_id", back_populates="doctor")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def has_role(self, role_name: Union[str, RoleEnum]) -> bool:
        target = role_name.value if isinstance(role_name, RoleEnum) else str(role_name)
        return any(
            (r.name.value if isinstance(r.name, RoleEnum) else str(r.name)) == target
            for r in self.roles
        )
