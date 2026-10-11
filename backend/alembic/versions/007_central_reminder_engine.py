"""Schema for reminders, reminder_logs, and notification_preferences.

Revision ID: 007_central_reminders
Revises: 006_prescriptions_and_medicines
Create Date: 2026-08-27 18:34:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "007_central_reminders"
down_revision: Union[str, None] = "006_prescriptions_and_medicines"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create reminders table
    op.create_table(
        "reminders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reminder_type", sa.String(length=50), server_default="CUSTOM", nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("recurrence", sa.String(length=50), server_default="ONCE", nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("due_time", sa.String(length=10), server_default="09:00", nullable=False),
        sa.Column("days_of_week", sa.String(length=50), server_default="DAILY", nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("reference_id", sa.String(length=100), nullable=True),
        sa.Column("reference_type", sa.String(length=50), nullable=True),
        sa.Column("metadata_info", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reminders_user_id", "reminders", ["user_id"])
    op.create_index("ix_reminders_reminder_type", "reminders", ["reminder_type"])
    op.create_index("ix_reminders_is_active", "reminders", ["is_active"])

    # Create reminder_logs table
    op.create_table(
        "reminder_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("reminder_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reminders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=50), server_default="PENDING", nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reminder_logs_reminder_id", "reminder_logs", ["reminder_id"])
    op.create_index("ix_reminder_logs_user_id", "reminder_logs", ["user_id"])
    op.create_index("ix_reminder_logs_scheduled_at", "reminder_logs", ["scheduled_at"])

    # Create notification_preferences table
    op.create_table(
        "notification_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("enable_in_app", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("enable_email", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("enable_push", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("medicine_alerts", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("refill_alerts", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("appointment_alerts", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("wellness_nudges", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("quiet_hours_start", sa.String(length=10), server_default="22:00", nullable=True),
        sa.Column("quiet_hours_end", sa.String(length=10), server_default="07:00", nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_notification_preferences_user_id", "notification_preferences", ["user_id"])

def downgrade() -> None:
    op.drop_table("notification_preferences")
    op.drop_table("reminder_logs")
    op.drop_table("reminders")
