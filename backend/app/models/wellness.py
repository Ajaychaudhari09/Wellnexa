import enum
import uuid
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Integer, Boolean, Date, DateTime, Enum, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class EmotionEnum(str, enum.Enum):
    HAPPY = "HAPPY"
    CALM = "CALM"
    CONTENT = "CONTENT"
    ENERGETIC = "ENERGETIC"
    FOCUSED = "FOCUSED"
    NEUTRAL = "NEUTRAL"
    TIRED = "TIRED"
    ANXIOUS = "ANXIOUS"
    STRESSED = "STRESSED"
    SAD = "SAD"
    OVERWHELMED = "OVERWHELMED"

class MoodLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "mood_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mood_score: Mapped[int] = mapped_column(Integer, nullable=False) # 1 (Very Low) to 5 (Great)
    primary_emotion: Mapped[EmotionEnum] = mapped_column(Enum(EmotionEnum, name="emotion_enum", native_enum=False), default=EmotionEnum.CONTENT, nullable=False)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True) # e.g. ["Work", "Exercise", "Family"]
    journal_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gratitude_note: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sleep_quality: Mapped[Optional[int]] = mapped_column(Integer, default=3, nullable=True) # 1 to 5
    logged_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False, index=True)
    crisis_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="mood_logs")
