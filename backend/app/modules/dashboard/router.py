from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.modules.dashboard.schemas import HomeDashboardResponse
from app.modules.dashboard.service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Intelligent Health Dashboard"])

@router.get("/home", response_model=ApiResponse[HomeDashboardResponse], status_code=status.HTTP_200_OK)
async def get_home_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[HomeDashboardResponse]:
    """Retrieve unified home dashboard aggregating medicines, reminders, vitals, nutrition, latest report, mood, and adherence widgets."""
    service = DashboardService(db)
    dashboard_data = await service.get_home_dashboard(current_user.id)
    return ApiResponse[HomeDashboardResponse](
        success=True,
        message="Home dashboard data retrieved successfully",
        data=dashboard_data,
    )
