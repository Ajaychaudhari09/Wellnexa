import uuid
from datetime import datetime, date, timedelta, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.core.exceptions import NotFoundException, WellNexaException
from app.models.wellness import MoodLog, EmotionEnum
from app.models.timeline import TimelineCategoryEnum, TimelineEventTypeEnum
from app.models.audit import AuditLog
from ai.mental_wellness.safety_checker import CrisisSafetyChecker
from app.modules.timeline.service import TimelineService
from app.modules.wellness.schemas import (
    MoodLogCreateRequest,
    MoodLogResponse,
    CrisisSupportInfo,
    WeeklyMoodTrendItem,
    WeeklyMoodTrendsResponse,
)

class WellnessService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.timeline_service = TimelineService(db)

    async def log_mood(self, user_id: uuid.UUID, req: MoodLogCreateRequest) -> MoodLogResponse:
        t_date = req.logged_date or datetime.now(timezone.utc).date()

        # Check for crisis keywords
        safety_check = CrisisSafetyChecker.evaluate_text(req.journal_text)
        is_crisis = safety_check["is_crisis_detected"]

        mood = MoodLog(
            user_id=user_id,
            mood_score=req.mood_score,
            primary_emotion=req.primary_emotion,
            tags=req.tags or [],
            journal_text=req.journal_text.strip() if req.journal_text else None,
            gratitude_note=req.gratitude_note.strip() if req.gratitude_note else None,
            sleep_quality=req.sleep_quality,
            logged_date=t_date,
            crisis_flag=is_crisis,
        )
        self.db.add(mood)
        await self.db.flush()

        # Emit timeline event
        emotion_str = req.primary_emotion.value.replace("_", " ").title()
        await self.timeline_service.record_event(
            user_id=user_id,
            category=TimelineCategoryEnum.WELLNESS,
            event_type=TimelineEventTypeEnum.SYSTEM_NOTICE,
            title=f"Mood Logged: {emotion_str} ({req.mood_score}/5)",
            summary=f"Emotion: {emotion_str} • Gratitude: '{req.gratitude_note or 'None logged'}'",
            occurred_at=datetime.now(timezone.utc),
            reference_id=str(mood.id),
            reference_type="mood_log",
        )

        crisis_info = None
        crisis_resources_dict = None
        if is_crisis:
            crisis_info = CrisisSupportInfo(
                support_message=safety_check["support_message"],
                helpline_resources=safety_check["helpline_resources"],
            )
            crisis_resources_dict = {
                "support_message": safety_check["support_message"],
                "hotlines": list(safety_check["helpline_resources"].values()),
                **safety_check["helpline_resources"],
            }

        return MoodLogResponse(
            id=mood.id,
            user_id=mood.user_id,
            mood_score=mood.mood_score,
            primary_emotion=mood.primary_emotion.value,
            tags=mood.tags or [],
            journal_text=mood.journal_text,
            gratitude_note=mood.gratitude_note,
            sleep_quality=mood.sleep_quality,
            logged_date=mood.logged_date,
            crisis_flag=mood.crisis_flag,
            is_crisis_detected=is_crisis,
            crisis_support=crisis_info,
            crisis_resources=crisis_resources_dict,
            created_at=mood.created_at,
        )

    async def get_mood_logs(self, user_id: uuid.UUID, limit: int = 30) -> List[MoodLog]:
        query = select(MoodLog).where(MoodLog.user_id == user_id).order_by(desc(MoodLog.logged_date)).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_today_mood(self, user_id: uuid.UUID) -> Optional[MoodLog]:
        today = datetime.now(timezone.utc).date()
        query = select(MoodLog).where(
            and_(MoodLog.user_id == user_id, MoodLog.logged_date == today)
        ).order_by(desc(MoodLog.created_at)).limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_weekly_mood_trends(self, user_id: uuid.UUID, days: int = 7) -> WeeklyMoodTrendsResponse:
        today = datetime.now(timezone.utc).date()
        trend_items: List[WeeklyMoodTrendItem] = []
        emotions: List[str] = []
        scores: List[int] = []

        for i in range(days - 1, -1, -1):
            d = today - timedelta(days=i)
            q = select(MoodLog).where(
                and_(MoodLog.user_id == user_id, MoodLog.logged_date == d)
            ).order_by(desc(MoodLog.created_at)).limit(1)
            res = await self.db.execute(q)
            m = res.scalar_one_or_none()

            if m:
                scores.append(m.mood_score)
                emotions.append(m.primary_emotion.value)
                trend_items.append(
                    WeeklyMoodTrendItem(
                        date=d,
                        day_name=d.strftime("%a"),
                        mood_score=m.mood_score,
                        primary_emotion=m.primary_emotion.value,
                        sleep_quality=m.sleep_quality,
                    )
                )
            else:
                trend_items.append(
                    WeeklyMoodTrendItem(
                        date=d,
                        day_name=d.strftime("%a"),
                        mood_score=None,
                        primary_emotion=None,
                        sleep_quality=None,
                    )
                )

        avg_score = round(sum(scores) / len(scores), 1) if scores else 3.0
        predom = max(set(emotions), key=emotions.count) if emotions else "CALM"

        return WeeklyMoodTrendsResponse(
            average_mood_score=avg_score,
            predominant_emotion=predom,
            total_entries_this_week=len(scores),
            trends=trend_items,
        )
