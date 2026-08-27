"""Schema for medical_documents.

Revision ID: 004_document_management
Revises: 003_health_timeline
Create Date: 2026-08-27 18:27:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004_document_management"
down_revision: Union[str, None] = "003_health_timeline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "medical_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(length=50), server_default="MEDICAL_REPORT", nullable=False),
        sa.Column("status", sa.String(length=50), server_default="UPLOADED", nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("original_file_name", sa.String(length=255), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("metadata_info", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_medical_documents_user_id", "medical_documents", ["user_id"])
    op.create_index("ix_medical_documents_category", "medical_documents", ["category"])
    op.create_index("ix_medical_documents_status", "medical_documents", ["status"])
    op.create_index("ix_medical_documents_checksum_sha256", "medical_documents", ["checksum_sha256"])
    op.create_index("ix_medical_documents_uploaded_at", "medical_documents", ["uploaded_at"])

def downgrade() -> None:
    op.drop_table("medical_documents")
