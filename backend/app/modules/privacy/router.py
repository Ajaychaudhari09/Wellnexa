import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.modules.privacy.schemas import (
    UserConsentResponse,
    UserConsentUpdateRequest,
    AccessAuditLogResponse,
    HealthDataExportResponse,
    DeleteAccountRequest,
)
from app.modules.privacy.service import PrivacyService

router = APIRouter(prefix="/privacy", tags=["Consent & Privacy Center"])

@router.get("/consent", response_model=ApiResponse[UserConsentResponse], status_code=status.HTTP_200_OK)
async def get_consent_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[UserConsentResponse]:
    """Retrieve patient consent preferences (AI analysis, anonymized insights, doctor sharing)."""
    service = PrivacyService(db)
    consent = await service.get_or_create_consent(current_user.id)
    payload = UserConsentResponse.model_validate(consent)
    return ApiResponse[UserConsentResponse](success=True, message="Consent settings retrieved", data=payload)

@router.put("/consent", response_model=ApiResponse[UserConsentResponse], status_code=status.HTTP_200_OK)
async def update_consent_settings(
    req: UserConsentUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[UserConsentResponse]:
    """Update patient consent preferences."""
    service = PrivacyService(db)
    consent = await service.update_consent(current_user.id, req)
    payload = UserConsentResponse.model_validate(consent)
    return ApiResponse[UserConsentResponse](success=True, message="Consent settings updated", data=payload)

@router.get("/access-logs", response_model=ApiResponse[List[AccessAuditLogResponse]], status_code=status.HTTP_200_OK)
async def get_access_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[AccessAuditLogResponse]]:
    """Retrieve audit log history of all clinical access, data exports, and doctor reviews."""
    service = PrivacyService(db)
    logs = await service.get_access_audit_logs(current_user.id, limit=limit)
    payload = [AccessAuditLogResponse.model_validate(l) for l in logs]
    return ApiResponse[List[AccessAuditLogResponse]](success=True, message="Access logs retrieved", data=payload)

@router.get("/export", response_model=ApiResponse[HealthDataExportResponse], status_code=status.HTTP_200_OK)
async def export_health_data(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[HealthDataExportResponse]:
    """Export complete patient personal health record archive in portable JSON format (GDPR/HIPAA)."""
    service = PrivacyService(db)
    client_ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    archive = await service.export_complete_health_data(current_user.id, ip_address=client_ip, user_agent=ua)
    return ApiResponse[HealthDataExportResponse](success=True, message="Health data archive generated", data=archive)

@router.post("/delete-account", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def delete_user_account(
    req: DeleteAccountRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    """Permanently delete user account and cascade purge all personal health data and documents."""
    service = PrivacyService(db)
    await service.delete_user_account_and_data(current_user.id, req.confirmation_password)
    return ApiResponse[dict](success=True, message="Account and personal health data purged permanently.", data={"status": "DELETED"})
