"""Schema for patient_access_grants and doctor_consultations.

Revision ID: 012_doctor_portal_and_access_grants
Revises: 011_chat_and_ai_assistant
Create Date: 2026-08-27 18:42:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "012_doctor_portal_and_access_grants"
down_revision: Union[str, None] = "011_chat_and_ai_assistant"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create patient_access_grants table
    op.create_table(
        "patient_access_grants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("access_token", sa.String(length=100), unique=True, nullable=False),
        sa.Column("access_scope", sa.String(length=50), server_default="FULL_ACCESS", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=50), server_default="ACTIVE", nullable=False),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_patient_access_grants_patient_id", "patient_access_grants", ["patient_id"])
    op.create_index("ix_patient_access_grants_doctor_id", "patient_access_grants", ["doctor_id"])
    op.create_index("ix_patient_access_grants_access_token", "patient_access_grants", ["access_token"])
    op.create_index("ix_patient_access_grants_expires_at", "patient_access_grants", ["expires_at"])
    op.create_index("ix_patient_access_grants_status", "patient_access_grants", ["status"])

    # Create doctor_consultations table
    op.create_table(
        "doctor_consultations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("doctor_name", sa.String(length=150), nullable=False),
        sa.Column("clinic_name", sa.String(length=150), nullable=True),
        sa.Column("consultation_date", sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column("chief_complaint", sa.String(length=300), nullable=False),
        sa.Column("clinical_observations", sa.Text(), nullable=True),
        sa.Column("recommended_actions", sa.Text(), nullable=True),
        sa.Column("follow_up_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_doctor_consultations_patient_id", "doctor_consultations", ["patient_id"])
    op.create_index("ix_doctor_consultations_doctor_id", "doctor_consultations", ["doctor_id"])
    op.create_index("ix_doctor_consultations_consultation_date", "doctor_consultations", ["consultation_date"])

def downgrade() -> None:
    op.drop_table("doctor_consultations")
    op.drop_table("patient_access_grants")
