"""Schema for medical_reports and report_extractions.

Revision ID: 005_ocr_and_reports
Revises: 004_document_management
Create Date: 2026-08-27 18:29:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "005_ocr_and_reports"
down_revision: Union[str, None] = "004_document_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create medical_reports table
    op.create_table(
        "medical_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("medical_documents.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("report_type", sa.String(length=50), server_default="GENERAL_LAB_REPORT", nullable=False),
        sa.Column("report_date", sa.Date(), nullable=True),
        sa.Column("lab_name", sa.String(length=150), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="PENDING_CONFIRMATION", nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("summary_notes", sa.String(length=500), nullable=True),
        sa.Column("metadata_info", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_medical_reports_user_id", "medical_reports", ["user_id"])
    op.create_index("ix_medical_reports_document_id", "medical_reports", ["document_id"])
    op.create_index("ix_medical_reports_report_type", "medical_reports", ["report_type"])
    op.create_index("ix_medical_reports_status", "medical_reports", ["status"])

    # Create report_extractions table
    op.create_table(
        "report_extractions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("medical_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("test_name", sa.String(length=150), nullable=False),
        sa.Column("metric_type", sa.String(length=100), nullable=True),
        sa.Column("detected_value", sa.Float(), nullable=False),
        sa.Column("confirmed_value", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("reference_range_low", sa.Float(), nullable=True),
        sa.Column("reference_range_high", sa.Float(), nullable=True),
        sa.Column("flag_status", sa.String(length=50), server_default="NORMAL", nullable=False),
        sa.Column("is_confirmed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("user_corrected", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_report_extractions_report_id", "report_extractions", ["report_id"])
    op.create_index("ix_report_extractions_metric_type", "report_extractions", ["metric_type"])

def downgrade() -> None:
    op.drop_table("report_extractions")
    op.drop_table("medical_reports")
