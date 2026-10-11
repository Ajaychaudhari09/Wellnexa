"""Schema for user_consents and access_audit_logs.

Revision ID: 013_consent_and_privacy
Revises: 012_doctor_portal_and_access_grants
Create Date: 2026-08-27 18:44:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "013_consent_and_privacy"
down_revision: Union[str, None] = "012_doctor_portal_and_access_grants"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create user_consents table
    op.create_table(
        "user_consents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("allow_ai_analysis", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("allow_anonymized_insights", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("allow_doctor_sharing", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("data_retention_days", sa.Integer(), server_default="365", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_consents_user_id", "user_consents", ["user_id"])

    # Create access_audit_logs table
    op.create_table(
        "access_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_role", sa.String(length=50), server_default="PATIENT", nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource", sa.String(length=100), nullable=False),
        sa.Column("ip_address", sa.String(length=50), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_access_audit_logs_user_id", "access_audit_logs", ["user_id"])
    op.create_index("ix_access_audit_logs_action", "access_audit_logs", ["action"])

def downgrade() -> None:
    op.drop_table("access_audit_logs")
    op.drop_table("user_consents")
