"""Schema for prescriptions, medications, medication_schedules, and medication_logs.

Revision ID: 006_prescriptions_and_medicines
Revises: 005_ocr_and_reports
Create Date: 2026-08-27 18:32:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "006_prescriptions_and_medicines"
down_revision: Union[str, None] = "005_ocr_and_reports"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create prescriptions table
    op.create_table(
        "prescriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("medical_documents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("doctor_name", sa.String(length=150), nullable=True),
        sa.Column("clinic_name", sa.String(length=150), nullable=True),
        sa.Column("prescribed_date", sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column("diagnosis_notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_prescriptions_user_id", "prescriptions", ["user_id"])
    op.create_index("ix_prescriptions_document_id", "prescriptions", ["document_id"])

    # Create medications table
    op.create_table(
        "medications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prescription_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prescriptions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("dosage", sa.String(length=100), nullable=False),
        sa.Column("form", sa.String(length=50), server_default="TABLET", nullable=False),
        sa.Column("frequency", sa.String(length=50), server_default="ONCE_DAILY", nullable=False),
        sa.Column("timing", sa.String(length=50), server_default="AFTER_MEAL", nullable=False),
        sa.Column("instructions", sa.String(length=300), nullable=True),
        sa.Column("start_date", sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("current_stock", sa.Integer(), server_default="30", nullable=False),
        sa.Column("refill_threshold", sa.Integer(), server_default="5", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_medications_user_id", "medications", ["user_id"])
    op.create_index("ix_medications_prescription_id", "medications", ["prescription_id"])
    op.create_index("ix_medications_name", "medications", ["name"])
    op.create_index("ix_medications_is_active", "medications", ["is_active"])

    # Create medication_schedules table
    op.create_table(
        "medication_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("medication_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("medications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("time_slot", sa.String(length=10), nullable=False),
        sa.Column("dosage_quantity", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("days_of_week", sa.String(length=50), server_default="DAILY", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_medication_schedules_medication_id", "medication_schedules", ["medication_id"])

    # Create medication_logs table
    op.create_table(
        "medication_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("medication_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("medications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=50), server_default="SCHEDULED", nullable=False),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_medication_logs_medication_id", "medication_logs", ["medication_id"])
    op.create_index("ix_medication_logs_user_id", "medication_logs", ["user_id"])
    op.create_index("ix_medication_logs_scheduled_at", "medication_logs", ["scheduled_at"])
    op.create_index("ix_medication_logs_status", "medication_logs", ["status"])

def downgrade() -> None:
    op.drop_table("medication_logs")
    op.drop_table("medication_schedules")
    op.drop_table("medications")
    op.drop_table("prescriptions")
