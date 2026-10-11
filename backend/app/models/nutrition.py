import enum
import uuid
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Float, Integer, Boolean, Date, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class MealTypeEnum(str, enum.Enum):
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"
    SNACK = "SNACK"
    PRE_WORKOUT = "PRE_WORKOUT"
    POST_WORKOUT = "POST_WORKOUT"

class DietTypeEnum(str, enum.Enum):
    VEGETARIAN = "VEGETARIAN"
    VEGAN = "VEGAN"
    NON_VEGETARIAN = "NON_VEGETARIAN"
    EGGETARIAN = "EGGETARIAN"
    KETO = "KETO"
    PALEO = "PALEO"
    JAIN = "JAIN"

class FoodItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "food_items"

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    serving_size: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    serving_unit: Mapped[str] = mapped_column(String(50), default="g", nullable=False)
    calories_kcal: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    carbs_g: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fat_g: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fiber_g: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), default="General", nullable=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

class MealLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "meal_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    meal_type: Mapped[MealTypeEnum] = mapped_column(Enum(MealTypeEnum, name="meal_type_enum", native_enum=False), default=MealTypeEnum.BREAKFAST, nullable=False, index=True)
    logged_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False, index=True)
    total_calories: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_protein: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_carbs: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_fat: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="meal_logs")
    items: Mapped[List["MealLogItem"]] = relationship("MealLogItem", back_populates="meal_log", cascade="all, delete-orphan", lazy="selectin")

class MealLogItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "meal_log_items"

    meal_log_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meal_logs.id", ondelete="CASCADE"), nullable=False, index=True)
    food_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("food_items.id", ondelete="SET NULL"), nullable=True)
    food_name: Mapped[str] = mapped_column(String(150), nullable=False)
    serving_quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    serving_unit: Mapped[str] = mapped_column(String(50), default="serving", nullable=False)
    calories_kcal: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    carbs_g: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fat_g: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    meal_log: Mapped["MealLog"] = relationship("MealLog", back_populates="items")

class NutritionTarget(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "nutrition_targets"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    calorie_target_kcal: Mapped[float] = mapped_column(Float, default=2000.0, nullable=False)
    protein_target_g: Mapped[float] = mapped_column(Float, default=75.0, nullable=False)
    carbs_target_g: Mapped[float] = mapped_column(Float, default=250.0, nullable=False)
    fat_target_g: Mapped[float] = mapped_column(Float, default=65.0, nullable=False)
    water_target_liters: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="nutrition_targets")

class MealPlan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "meal_plans"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    goal: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. WEIGHT_MANAGEMENT, MUSCLE_GAIN
    diet_type: Mapped[DietTypeEnum] = mapped_column(Enum(DietTypeEnum, name="diet_type_enum", native_enum=False), default=DietTypeEnum.VEGETARIAN, nullable=False)
    cuisine_preference: Mapped[str] = mapped_column(String(100), default="INDIAN", nullable=False)
    target_calories: Mapped[float] = mapped_column(Float, nullable=False)
    plan_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="meal_plans")
    grocery_lists: Mapped[List["GroceryList"]] = relationship("GroceryList", back_populates="meal_plan", cascade="all, delete-orphan")

class GroceryList(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "grocery_lists"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    meal_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("meal_plans.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    items_data: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="grocery_lists")
    meal_plan: Mapped[Optional["MealPlan"]] = relationship("MealPlan", back_populates="grocery_lists")
