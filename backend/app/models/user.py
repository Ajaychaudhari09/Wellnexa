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
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    metrics: Mapped[List["HealthMetric"]] = relationship("HealthMetric", back_populates="user", cascade="all, delete-orphan")
    allergies: Mapped[List["Allergy"]] = relationship("Allergy", back_populates="user", cascade="all, delete-orphan")
    conditions: Mapped[List["MedicalCondition"]] = relationship("MedicalCondition", back_populates="user", cascade="all, delete-orphan")
    goals: Mapped[List["HealthGoal"]] = relationship("HealthGoal", back_populates="user", cascade="all, delete-orphan")
    timeline_events: Mapped[List["HealthTimelineEvent"]] = relationship("HealthTimelineEvent", back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[List["MedicalDocument"]] = relationship("MedicalDocument", back_populates="user", cascade="all, delete-orphan")

    def has_role(self, role_name: Union[str, RoleEnum]) -> bool:
        target = role_name.value if isinstance(role_name, RoleEnum) else str(role_name)
        return any(
            (r.name.value if isinstance(r.name, RoleEnum) else str(r.name)) == target
            for r in self.roles
        )
