import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.models.health import MetricTypeEnum
from app.modules.health.schemas import (
    MetricCreateItem,
    MetricBatchCreateRequest,
    MetricResponse,
    MetricTrendResponse,
)
from app.modules.health.service import HealthMetricService

router = APIRouter(prefix="/metrics", tags=["Health Metrics"])

@router.post("", response_model=ApiResponse[List[MetricResponse]], status_code=status.HTTP_201_CREATED)
async def log_metrics(
    req: MetricBatchCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[MetricResponse]]:
    """Log one or multiple health metrics with automatic BMI calculation."""
    service = HealthMetricService(db)
    created = await service.log_metrics(current_user.id, req.metrics)

    payload = [
        MetricResponse(
            id=m.id,
            user_id=m.user_id,
            metric_type=m.metric_type.value if hasattr(m.metric_type, "value") else str(m.metric_type),
            value=m.value,
            unit=m.unit,
            recorded_at=m.recorded_at,
            source=m.source.value if hasattr(m.source, "value") else str(m.source),
            notes=m.notes,
        )
        for m in created
    ]

    return ApiResponse[List[MetricResponse]](
        success=True,
        message="Metrics logged successfully",
        data=payload,
    )

@router.get("", response_model=ApiResponse[List[MetricResponse]], status_code=status.HTTP_200_OK)
async def get_metrics(
    metric_type: Optional[MetricTypeEnum] = Query(None, description="Filter by metric type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter (UTC)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (UTC)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[MetricResponse]]:
    """Retrieve logged health metrics with optional type and date filtering."""
    service = HealthMetricService(db)
    metrics = await service.get_metrics(
        user_id=current_user.id,
        metric_type=metric_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    payload = [
        MetricResponse(
            id=m.id,
            user_id=m.user_id,
            metric_type=m.metric_type.value if hasattr(m.metric_type, "value") else str(m.metric_type),
            value=m.value,
            unit=m.unit,
            recorded_at=m.recorded_at,
            source=m.source.value if hasattr(m.source, "value") else str(m.source),
            notes=m.notes,
        )
        for m in metrics
    ]

    return ApiResponse[List[MetricResponse]](
        success=True,
        message="Metrics retrieved successfully",
        data=payload,
    )

@router.get("/trends/{metric_type}", response_model=ApiResponse[MetricTrendResponse], status_code=status.HTTP_200_OK)
async def get_metric_trends(
    metric_type: MetricTypeEnum,
    days: int = Query(30, ge=1, le=365, description="Lookback window in days"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MetricTrendResponse]:
    """Retrieve historical metric trends, minimum, maximum, and average values for charts."""
    service = HealthMetricService(db)
    trends = await service.get_metric_trends(current_user.id, metric_type, days=days)

    return ApiResponse[MetricTrendResponse](
        success=True,
        message="Metric trends calculated successfully",
        data=trends,
    )

@router.delete("/{metric_id}", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def delete_metric(
    metric_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    """Delete a logged health metric entry."""
    service = HealthMetricService(db)
    await service.delete_metric(current_user.id, metric_id)

    return ApiResponse[dict](
        success=True,
        message="Metric deleted successfully",
        data={"id": str(metric_id)},
    )
