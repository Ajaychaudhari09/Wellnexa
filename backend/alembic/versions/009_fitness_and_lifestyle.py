"""Schema for workout_logs, daily_activity_summaries, habits, and habit_logs.

Revision ID: 009_fitness_and_lifestyle
Revises: 008_nutrition_and_meals
Create Date: 2026-08-27 18:37:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "009_fitness_and_lifestyle"
down_revision: Union[str, None] = "008_nutrition_and_meals"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create workout_logs table
    op.create_table(
        "workout_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("activity_type", sa.String(length=50), server_default="CUSTOM", nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("calories_burned", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("intensity", sa.String(length=50), server_default="MODERATE", nullable=False),
        sa.Column("distance_km", sa.Float(), nullable=True),
        sa.Column("heart_rate_avg", sa.Integer(), nullable=True),
        sa.Column("logged_date", sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column("notes", sa.String(length=300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_workout_logs_user_id", "workout_logs", ["user_id"])
    op.create_index("ix_workout_logs_activity_type", "workout_logs", ["activity_type"])
    op.create_index("ix_workout_logs_logged_date", "workout_logs", ["logged_date"])

    # Create daily_activity_summaries table
    op.create_table(
        "daily_activity_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column("steps", sa.Integer(), server_default="0", nullable=False),
        sa.Column("active_minutes", sa.Integer(), server_default="0", nullable=False),
        sa.Column("calories_burned", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("water_ml", sa.Integer(), server_default="0", nullable=False),
        sa.Column("sleep_hours", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("sleep_quality", sa.Integer(), server_default="3", nullable=True),
        sa.Column("stress_level", sa.Integer(), server_default="5", nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_daily_activity_summaries_user_id", "daily_activity_summaries", ["user_id"])
    op.create_index("ix_daily_activity_summaries_date", "daily_activity_summaries", ["date"])

    # Create habits table
    op.create_table(
        "habits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.String(length=300), nullable=True),
        sa.Column("category", sa.String(length=50), server_default="General", nullable=False),
        sa.Column("frequency", sa.String(length=50), server_default="DAILY", nullable=False),
        sa.Column("current_streak", sa.Integer(), server_default="0", nullable=False),
        sa.Column("longest_streak", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_habits_user_id", "habits", ["user_id"])
    op.create_index("ix_habits_is_active", "habits", ["is_active"])

    # Create habit_logs table
    op.create_table(
        "habit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("habit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("habits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("logged_date", sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column("is_completed", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_habit_logs_habit_id", "habit_logs", ["habit_id"])
    op.create_index("ix_habit_logs_user_id", "habit_logs", ["user_id"])
    op.create_index("ix_habit_logs_logged_date", "habit_logs", ["logged_date"])

def downgrade() -> None:
    op.drop_table("habit_logs")
    op.drop_table("habits")
    op.drop_table("daily_activity_summaries")
    op.drop_table("workout_logs")
