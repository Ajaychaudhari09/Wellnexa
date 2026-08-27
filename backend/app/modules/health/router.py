from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
from app.schemas.common import ApiResponse, HealthStatus

router = APIRouter(prefix="/health", tags=["System Health"])

@router.get("", response_model=ApiResponse[HealthStatus], status_code=status.HTTP_200_OK)
async def check_health(db: AsyncSession = Depends(get_db)) -> ApiResponse[HealthStatus]:
    """Perform system health, configuration, and database connection checks."""
    db_status = "healthy"
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    overall_status = "healthy" if db_status == "healthy" else "degraded"

    payload = HealthStatus(
        status=overall_status,
        environment=settings.ENVIRONMENT,
        version="0.1.0",
        timestamp=datetime.now(timezone.utc),
        database=db_status,
    )

    return ApiResponse[HealthStatus](
        success=overall_status == "healthy",
        message="System health check executed.",
        data=payload,
    )
