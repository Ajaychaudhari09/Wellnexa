import uuid
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_roles
from app.schemas.common import ApiResponse
from app.models.user import User, RoleEnum
from app.modules.audit.schemas import (
    PatientActivitySummaryResponse,
    AdminAuditLogListResponse,
)
from app.modules.audit.service import AuditService

router = APIRouter(prefix="/audit", tags=["Immutable Audit & Compliance Logging"])

@router.get("/me", response_model=ApiResponse[PatientActivitySummaryResponse], status_code=status.HTTP_200_OK)
async def get_my_security_activity(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PatientActivitySummaryResponse]:
    """Retrieve patient security activity feed (logins, doctor shares, data exports)."""
    service = AuditService(db)
    activity = await service.get_patient_activity_stream(current_user.id, limit=limit)
    return ApiResponse[PatientActivitySummaryResponse](
        success=True,
        message="Patient activity stream retrieved",
        data=activity,
    )

@router.get("/admin", response_model=ApiResponse[AdminAuditLogListResponse], status_code=status.HTTP_200_OK)
async def query_compliance_audit_logs(
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action name"),
    resource: Optional[str] = Query(None, description="Filter by resource type"),
    start_date: Optional[date] = Query(None, description="Filter from start date"),
    end_date: Optional[date] = Query(None, description="Filter to end date"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(RoleEnum.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminAuditLogListResponse]:
    """Admin compliance audit search and filtering (Protected: ADMIN role only)."""
    service = AuditService(db)
    logs = await service.query_admin_audit_logs(
        user_id=user_id,
        action=action,
        resource=resource,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return ApiResponse[AdminAuditLogListResponse](
        success=True,
        message="Compliance audit logs retrieved",
        data=logs,
    )
