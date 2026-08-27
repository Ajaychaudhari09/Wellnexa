import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.core.exceptions import NotFoundException
from app.models.timeline import HealthTimelineEvent, TimelineCategoryEnum, TimelineEventTypeEnum
from app.modules.timeline.schemas import TimelineCustomEventRequest

class TimelineService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_event(
        self,
        user_id: uuid.UUID,
        category: TimelineCategoryEnum,
        event_type: TimelineEventTypeEnum,
        title: str,
        summary: Optional[str] = None,
        occurred_at: Optional[datetime] = None,
        reference_id: Optional[str] = None,
        reference_type: Optional[str] = None,
        metadata_info: Optional[Dict[str, Any]] = None,
        is_pinned: bool = False,
    ) -> HealthTimelineEvent:
        """Record an event into the central chronological health timeline."""
        event = HealthTimelineEvent(
            user_id=user_id,
            category=category,
            event_type=event_type,
            title=title,
            summary=summary,
            occurred_at=occurred_at or datetime.now(timezone.utc),
            reference_id=reference_id,
            reference_type=reference_type,
            metadata_info=metadata_info or {},
            is_pinned=is_pinned,
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_timeline_feed(
        self,
        user_id: uuid.UUID,
        category: Optional[TimelineCategoryEnum] = None,
        event_type: Optional[TimelineEventTypeEnum] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[HealthTimelineEvent], int, bool]:
        """Query user timeline with chronological ordering, category filters, and pagination."""
        query = select(HealthTimelineEvent).where(HealthTimelineEvent.user_id == user_id)

        if category:
            query = query.where(HealthTimelineEvent.category == category)
        if event_type:
            query = query.where(HealthTimelineEvent.event_type == event_type)
        if start_date:
            query = query.where(HealthTimelineEvent.occurred_at >= start_date)
        if end_date:
            query = query.where(HealthTimelineEvent.occurred_at <= end_date)

        # Count total
        count_q = select(func.count()).select_from(query.subquery())
        count_res = await self.db.execute(count_q)
        total_count = count_res.scalar() or 0

        # Sort pinned first, then newest first
        query = query.order_by(desc(HealthTimelineEvent.is_pinned), desc(HealthTimelineEvent.occurred_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        events = list(result.scalars().all())

        has_more = (offset + len(events)) < total_count
        return events, total_count, has_more

    async def pin_unpin_event(self, user_id: uuid.UUID, event_id: uuid.UUID, is_pinned: bool) -> HealthTimelineEvent:
        """Toggle pinned status for an important health timeline event."""
        query = select(HealthTimelineEvent).where(
            and_(HealthTimelineEvent.id == event_id, HealthTimelineEvent.user_id == user_id)
        )
        result = await self.db.execute(query)
        event = result.scalar_one_or_none()
        if not event:
            raise NotFoundException("HealthTimelineEvent", event_id)
        
        event.is_pinned = is_pinned
        await self.db.flush()
        return event

    async def create_custom_event(self, user_id: uuid.UUID, req: TimelineCustomEventRequest) -> HealthTimelineEvent:
        """Allow user to log custom health milestones or notes."""
        return await self.record_event(
            user_id=user_id,
            category=req.category,
            event_type=TimelineEventTypeEnum.CUSTOM_MILESTONE,
            title=req.title,
            summary=req.summary,
            occurred_at=req.occurred_at or datetime.now(timezone.utc),
            metadata_info=req.metadata_info,
        )
