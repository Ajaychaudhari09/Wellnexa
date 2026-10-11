"""Schema for mood_logs.

Revision ID: 010_mental_wellness_and_mood
Revises: 009_fitness_and_lifestyle
Create Date: 2026-08-27 18:39:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "010_mental_wellness_and_mood"
down_revision: Union[str, None] = "009_fitness_and_lifestyle"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create mood_logs table
    op.create_table(
        "mood_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mood_score", sa.Integer(), nullable=False),
        sa.Column("primary_emotion", sa.String(length=50), server_default="CONTENT", nullable=False),
        sa.Column("tags", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("journal_text", sa.Text(), nullable=True),
        sa.Column("gratitude_note", sa.String(length=500), nullable=True),
        sa.Column("sleep_quality", sa.Integer(), server_default="3", nullable=True),
        sa.Column("logged_date", sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column("crisis_flag", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_mood_logs_user_id", "mood_logs", ["user_id"])
    op.create_index("ix_mood_logs_logged_date", "mood_logs", ["logged_date"])

def downgrade() -> None:
    op.drop_table("mood_logs")
