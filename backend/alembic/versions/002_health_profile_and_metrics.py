"""Schema for health_metrics, allergies, medical_conditions, health_goals, and lifestyle_profiles.

Revision ID: 002_health_metrics
Revises: 001_initial_auth
Create Date: 2026-08-27 18:23:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002_health_metrics"
down_revision: Union[str, None] = "001_initial_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create health_metrics table
    op.create_table(
        "health_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("metric_type", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("source", sa.String(length=50), server_default="MANUAL", nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("metadata_info", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_health_metrics_user_id", "health_metrics", ["user_id"])
    op.create_index("ix_health_metrics_metric_type", "health_metrics", ["metric_type"])
    op.create_index("ix_health_metrics_recorded_at", "health_metrics", ["recorded_at"])

    # Create allergies table
    op.create_table(
        "allergies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("allergen", sa.String(length=150), nullable=False),
        sa.Column("reaction", sa.String(length=255), nullable=True),
        sa.Column("severity", sa.String(length=50), server_default="MODERATE", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_allergies_user_id", "allergies", ["user_id"])

    # Create medical_conditions table
    op.create_table(
        "medical_conditions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("condition_name", sa.String(length=150), nullable=False),
        sa.Column("diagnosed_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="ACTIVE", nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_medical_conditions_user_id", "medical_conditions", ["user_id"])

    # Create health_goals table
    op.create_table(
        "health_goals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("goal_type", sa.String(length=100), nullable=False),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column("current_value", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("start_date", sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="IN_PROGRESS", nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_health_goals_user_id", "health_goals", ["user_id"])

    # Create lifestyle_profiles table
    op.create_table(
        "lifestyle_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("diet_type", sa.String(length=100), server_default="OMNIVORE", nullable=False),
        sa.Column("activity_level", sa.String(length=100), server_default="MODERATE", nullable=False),
        sa.Column("smoking_status", sa.String(length=50), server_default="NON_SMOKER", nullable=False),
        sa.Column("alcohol_status", sa.String(length=50), server_default="OCCASIONAL", nullable=False),
        sa.Column("sleep_target_hours", sa.Float(), server_default="8.0", nullable=False),
        sa.Column("water_target_liters", sa.Float(), server_default="2.5", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_lifestyle_profiles_user_id", "lifestyle_profiles", ["user_id"])

def downgrade() -> None:
    op.drop_table("lifestyle_profiles")
    op.drop_table("health_goals")
    op.drop_table("medical_conditions")
    op.drop_table("allergies")
    op.drop_table("health_metrics")
