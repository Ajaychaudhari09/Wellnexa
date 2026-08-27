"""Schema for health_timeline_events.

Revision ID: 003_health_timeline
Revises: 002_health_metrics
Create Date: 2026-08-27 18:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003_health_timeline"
down_revision: Union[str, None] = "002_health_metrics"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "health_timeline_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(length=50), server_default="GENERAL", nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.String(length=500), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("reference_id", sa.String(length=100), nullable=True),
        sa.Column("reference_type", sa.String(length=50), nullable=True),
        sa.Column("metadata_info", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("is_pinned", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_health_timeline_events_user_id", "health_timeline_events", ["user_id"])
    op.create_index("ix_health_timeline_events_category", "health_timeline_events", ["category"])
    op.create_index("ix_health_timeline_events_event_type", "health_timeline_events", ["event_type"])
    op.create_index("ix_health_timeline_events_occurred_at", "health_timeline_events", ["occurred_at"])
    op.create_index("ix_health_timeline_events_reference_id", "health_timeline_events", ["reference_id"])

def downgrade() -> None:
    op.drop_table("health_timeline_events")
