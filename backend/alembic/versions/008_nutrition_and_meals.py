"""Schema for food_items, meal_logs, meal_log_items, nutrition_targets, meal_plans, and grocery_lists.

Revision ID: 008_nutrition_and_meals
Revises: 007_central_reminders
Create Date: 2026-08-27 18:36:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "008_nutrition_and_meals"
down_revision: Union[str, None] = "007_central_reminders"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create food_items table
    op.create_table(
        "food_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("serving_size", sa.Float(), server_default="100.0", nullable=False),
        sa.Column("serving_unit", sa.String(length=50), server_default="g", nullable=False),
        sa.Column("calories_kcal", sa.Float(), nullable=False),
        sa.Column("protein_g", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("carbs_g", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("fat_g", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("fiber_g", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("category", sa.String(length=100), server_default="General", nullable=True),
        sa.Column("is_custom", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_food_items_name", "food_items", ["name"])
    op.create_index("ix_food_items_user_id", "food_items", ["user_id"])

    # Create meal_logs table
    op.create_table(
        "meal_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("meal_type", sa.String(length=50), server_default="BREAKFAST", nullable=False),
        sa.Column("logged_date", sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column("total_calories", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("total_protein", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("total_carbs", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("total_fat", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("notes", sa.String(length=300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_meal_logs_user_id", "meal_logs", ["user_id"])
    op.create_index("ix_meal_logs_logged_date", "meal_logs", ["logged_date"])
    op.create_index("ix_meal_logs_meal_type", "meal_logs", ["meal_type"])

    # Create meal_log_items table
    op.create_table(
        "meal_log_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("meal_log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("meal_logs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("food_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("food_items.id", ondelete="SET NULL"), nullable=True),
        sa.Column("food_name", sa.String(length=150), nullable=False),
        sa.Column("serving_quantity", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("serving_unit", sa.String(length=50), server_default="serving", nullable=False),
        sa.Column("calories_kcal", sa.Float(), nullable=False),
        sa.Column("protein_g", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("carbs_g", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("fat_g", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_meal_log_items_meal_log_id", "meal_log_items", ["meal_log_id"])

    # Create nutrition_targets table
    op.create_table(
        "nutrition_targets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("calorie_target_kcal", sa.Float(), server_default="2000.0", nullable=False),
        sa.Column("protein_target_g", sa.Float(), server_default="75.0", nullable=False),
        sa.Column("carbs_target_g", sa.Float(), server_default="250.0", nullable=False),
        sa.Column("fat_target_g", sa.Float(), server_default="65.0", nullable=False),
        sa.Column("water_target_liters", sa.Float(), server_default="2.5", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_nutrition_targets_user_id", "nutrition_targets", ["user_id"])

    # Create meal_plans table
    op.create_table(
        "meal_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("goal", sa.String(length=100), nullable=False),
        sa.Column("diet_type", sa.String(length=50), server_default="VEGETARIAN", nullable=False),
        sa.Column("cuisine_preference", sa.String(length=100), server_default="INDIAN", nullable=False),
        sa.Column("target_calories", sa.Float(), nullable=False),
        sa.Column("plan_data", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_meal_plans_user_id", "meal_plans", ["user_id"])

    # Create grocery_lists table
    op.create_table(
        "grocery_lists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("meal_plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("meal_plans.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("items_data", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("is_completed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_grocery_lists_user_id", "grocery_lists", ["user_id"])

def downgrade() -> None:
    op.drop_table("grocery_lists")
    op.drop_table("meal_plans")
    op.drop_table("nutrition_targets")
    op.drop_table("meal_log_items")
    op.drop_table("meal_logs")
    op.drop_table("food_items")
