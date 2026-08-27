import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.models.timeline import TimelineCategoryEnum, TimelineEventTypeEnum
from app.modules.timeline.schemas import (
    TimelineCustomEventRequest,
    PinEventRequest,
    TimelineEventResponse,
    TimelineFeedResponse,
)
from app.modules.timeline.service import TimelineService

router = APIRouter(prefix="/timeline", tags=["Central Health Timeline"])

@router.get("", response_model=ApiResponse[TimelineFeedResponse], status_code=status.HTTP_200_OK)
async def get_timeline(
    category: Optional[TimelineCategoryEnum] = Query(None, description="Filter by category (CLINICAL, MEDICATION, FITNESS, WELLNESS, APPOINTMENT, REMINDER, GENERAL)"),
    event_type: Optional[TimelineEventTypeEnum] = Query(None, description="Filter by event type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter (UTC)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (UTC)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TimelineFeedResponse]:
    """Retrieve chronological health events feed with filtering and pagination."""
    service = TimelineService(db)
    events, total, has_more = await service.get_timeline_feed(
        user_id=current_user.id,
        category=category,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    payload = [
        TimelineEventResponse(
            id=e.id,
            user_id=e.user_id,
            category=e.category.value if hasattr(e.category, "value") else str(e.category),
            event_type=e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type),
            title=e.title,
            summary=e.summary,
            occurred_at=e.occurred_at,
            reference_id=e.reference_id,
            reference_type=e.reference_type,
            metadata_info=e.metadata_info,
            is_pinned=e.is_pinned,
        )
        for e in events
    ]

    feed = TimelineFeedResponse(
        events=payload,
        total_count=total,
        has_more=has_more,
    )

    return ApiResponse[TimelineFeedResponse](
        success=True,
        message="Timeline feed retrieved successfully",
        data=feed,
    )

@router.post("/custom", response_model=ApiResponse[TimelineEventResponse], status_code=status.HTTP_201_CREATED)
async def create_custom_timeline_event(
    req: TimelineCustomEventRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TimelineEventResponse]:
    """Manually record a custom health milestone or note in the timeline."""
    service = TimelineService(db)
    e = await service.create_custom_event(current_user.id, req)

    payload = TimelineEventResponse(
        id=e.id,
        user_id=e.user_id,
        category=e.category.value if hasattr(e.category, "value") else str(e.category),
        event_type=e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type),
        title=e.title,
        summary=e.summary,
        occurred_at=e.occurred_at,
        reference_id=e.reference_id,
        reference_type=e.reference_type,
        metadata_info=e.metadata_info,
        is_pinned=e.is_pinned,
    )

    return ApiResponse[TimelineEventResponse](
        success=True,
        message="Custom timeline event created",
        data=payload,
    )

@router.patch("/{event_id}/pin", response_model=ApiResponse[TimelineEventResponse], status_code=status.HTTP_200_OK)
async def toggle_pin_timeline_event(
    event_id: uuid.UUID,
    req: PinEventRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TimelineEventResponse]:
    """Pin or unpin a health timeline event."""
    service = TimelineService(db)
    e = await service.pin_unpin_event(current_user.id, event_id, req.is_pinned)

    payload = TimelineEventResponse(
        id=e.id,
        user_id=e.user_id,
        category=e.category.value if hasattr(e.category, "value") else str(e.category),
        event_type=e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type),
        title=e.title,
        summary=e.summary,
        occurred_at=e.occurred_at,
        reference_id=e.reference_id,
        reference_type=e.reference_type,
        metadata_info=e.metadata_info,
        is_pinned=e.is_pinned,
    )

    return ApiResponse[TimelineEventResponse](
        success=True,
        message=f"Event {'pinned' if req.is_pinned else 'unpinned'} successfully",
        data=payload,
    )
