from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.modules.snapshot.schemas import HealthSnapshotResponse
from app.modules.snapshot.service import SnapshotService

router = APIRouter(prefix="/snapshot", tags=["AI Health Snapshot"])

@router.get("", response_model=ApiResponse[HealthSnapshotResponse], status_code=status.HTTP_200_OK)
async def get_ai_health_snapshot(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[HealthSnapshotResponse]:
    """Generate or retrieve a holistic 360-degree AI Health Snapshot with positive trends, attention areas, and next actions."""
    service = SnapshotService(db)
    snapshot = await service.get_health_snapshot(current_user.id)
    return ApiResponse[HealthSnapshotResponse](
        success=True,
        message="AI Health Snapshot generated successfully",
        data=snapshot,
    )
