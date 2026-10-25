import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_optional_current_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.modules.doctor.schemas import (
    CreateAccessGrantRequest,
    AccessGrantResponse,
    DoctorConsultationCreateRequest,
    DoctorConsultationResponse,
    PatientClinicalSummaryResponse,
)
from app.modules.doctor.service import DoctorService

router = APIRouter(tags=["Doctor Portal & Time-Bound Sharing"])

# ----------------- Patient Sharing Controls -----------------
@router.post("/sharing/grants", response_model=ApiResponse[AccessGrantResponse], status_code=status.HTTP_201_CREATED)
async def create_access_grant(
    req: CreateAccessGrantRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AccessGrantResponse]:
    """Patient generates a secure, time-bound clinical access token/link for their doctor."""
    service = DoctorService(db)
    grant = await service.create_access_grant(current_user.id, req)
    return ApiResponse[AccessGrantResponse](success=True, message="Access grant created", data=grant)

@router.get("/sharing/grants", response_model=ApiResponse[List[AccessGrantResponse]], status_code=status.HTTP_200_OK)
async def list_access_grants(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[AccessGrantResponse]]:
    """List all active and historical access grants for current patient."""
    service = DoctorService(db)
    grants = await service.get_patient_grants(current_user.id)
    return ApiResponse[List[AccessGrantResponse]](success=True, message="Grants retrieved", data=grants)

@router.post("/sharing/grants/{grant_id}/revoke", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def revoke_access_grant(
    grant_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    """Instant kill switch: revoke an active doctor access grant immediately."""
    service = DoctorService(db)
    await service.revoke_access_grant(current_user.id, grant_id)
    return ApiResponse[dict](success=True, message="Access grant revoked successfully", data={"id": str(grant_id)})

# ----------------- Doctor Portal Endpoints -----------------
@router.get("/doctor/patient/{patient_id}/summary", response_model=ApiResponse[PatientClinicalSummaryResponse], status_code=status.HTTP_200_OK)
async def get_patient_summary_for_doctor(
    patient_id: uuid.UUID,
    token: str = Query(..., description="Time-bound access token from patient grant"),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PatientClinicalSummaryResponse]:
    """Doctor portal: view consolidated patient profile, vitals, medications, and confirmed reports."""
    service = DoctorService(db)
    summary = await service.get_patient_clinical_summary(access_token=token, patient_id=patient_id)
    return ApiResponse[PatientClinicalSummaryResponse](success=True, message="Patient summary retrieved", data=summary)

@router.post("/doctor/patient/{patient_id}/consultations", response_model=ApiResponse[DoctorConsultationResponse], status_code=status.HTTP_201_CREATED)
async def create_consultation_note(
    patient_id: uuid.UUID,
    req: DoctorConsultationCreateRequest,
    token: Optional[str] = Query(None, description="Access token if accessing via link"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DoctorConsultationResponse]:
    """Record clinical consultation observations and action plan, syncing to patient timeline."""
    service = DoctorService(db)
    # Validate token if not direct logged-in doctor
    if token:
        await service.validate_grant(token, patient_id)

    doc_id = current_user.id if current_user else None
    consultation = await service.create_consultation_note(patient_id=patient_id, req=req, doctor_id=doc_id)
    payload = DoctorConsultationResponse.model_validate(consultation)
    return ApiResponse[DoctorConsultationResponse](success=True, message="Consultation note saved", data=payload)

@router.get("/doctor/patient/{patient_id}/consultations", response_model=ApiResponse[List[DoctorConsultationResponse]], status_code=status.HTTP_200_OK)
async def get_patient_consultations(
    patient_id: uuid.UUID,
    token: Optional[str] = Query(None, description="Access token"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[DoctorConsultationResponse]]:
    """Retrieve consultation notes for a patient."""
    service = DoctorService(db)
    if token:
        await service.validate_grant(token, patient_id)

    consultations = await service.get_patient_consultations(patient_id)
    payload = [DoctorConsultationResponse.model_validate(c) for c in consultations]
    return ApiResponse[List[DoctorConsultationResponse]](success=True, message="Consultations retrieved", data=payload)
