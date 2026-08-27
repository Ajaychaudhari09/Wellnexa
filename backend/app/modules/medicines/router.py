import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.modules.medicines.schemas import (
    PrescriptionCreateRequest,
    PrescriptionResponse,
    MedicationCreateRequest,
    MedicationUpdateRequest,
    MedicationResponse,
    LogDoseRequest,
    MedicationLogResponse,
    TodayMedicationScheduleResponse,
    AdherenceScoreResponse,
    RefillAlertResponse,
)
from app.modules.medicines.service import MedicineService

router = APIRouter(tags=["Prescriptions & Medicine Manager"])

# ----------------- Prescriptions -----------------
@router.post("/prescriptions", response_model=ApiResponse[PrescriptionResponse], status_code=status.HTTP_201_CREATED)
async def create_prescription(
    req: PrescriptionCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PrescriptionResponse]:
    """Create a new digital prescription record."""
    service = MedicineService(db)
    presc = await service.create_prescription(current_user.id, req)
    payload = PrescriptionResponse.model_validate(presc)
    return ApiResponse[PrescriptionResponse](success=True, message="Prescription created", data=payload)

@router.get("/prescriptions", response_model=ApiResponse[List[PrescriptionResponse]], status_code=status.HTTP_200_OK)
async def get_prescriptions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[PrescriptionResponse]]:
    """Retrieve user's prescriptions."""
    service = MedicineService(db)
    prescriptions = await service.get_prescriptions(current_user.id)
    payload = [PrescriptionResponse.model_validate(p) for p in prescriptions]
    return ApiResponse[List[PrescriptionResponse]](success=True, message="Prescriptions retrieved", data=payload)

# ----------------- Medications -----------------
@router.post("/medicines", response_model=ApiResponse[MedicationResponse], status_code=status.HTTP_201_CREATED)
async def add_medication(
    req: MedicationCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MedicationResponse]:
    """Add a new medication with daily dosage schedules and stock inventory tracking."""
    service = MedicineService(db)
    med = await service.add_medication(current_user.id, req)
    payload = MedicationResponse.model_validate(med)
    return ApiResponse[MedicationResponse](success=True, message="Medication added successfully", data=payload)

@router.get("/medicines", response_model=ApiResponse[List[MedicationResponse]], status_code=status.HTTP_200_OK)
async def get_medications(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[MedicationResponse]]:
    """List medications with schedules and stock counts."""
    service = MedicineService(db)
    meds = await service.get_medications(current_user.id, is_active=is_active)
    payload = [MedicationResponse.model_validate(m) for m in meds]
    return ApiResponse[List[MedicationResponse]](success=True, message="Medications retrieved", data=payload)

@router.get("/medicines/today", response_model=ApiResponse[TodayMedicationScheduleResponse], status_code=status.HTTP_200_OK)
async def get_today_schedule(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TodayMedicationScheduleResponse]:
    """Retrieve today's medication dose schedule and taken/pending statuses."""
    service = MedicineService(db)
    schedule = await service.get_today_schedule(current_user.id)
    return ApiResponse[TodayMedicationScheduleResponse](success=True, message="Today's schedule retrieved", data=schedule)

@router.post("/medicines/{medication_id}/log-dose", response_model=ApiResponse[MedicationLogResponse], status_code=status.HTTP_200_OK)
async def log_dose(
    medication_id: uuid.UUID,
    req: LogDoseRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MedicationLogResponse]:
    """Log dose as TAKEN, MISSED, or SKIPPED, automatically updating inventory stock."""
    service = MedicineService(db)
    log = await service.log_dose(current_user.id, medication_id, req)
    payload = MedicationLogResponse.model_validate(log)
    return ApiResponse[MedicationLogResponse](success=True, message=f"Dose marked as {req.status.value}", data=payload)

@router.get("/medicines/adherence", response_model=ApiResponse[AdherenceScoreResponse], status_code=status.HTTP_200_OK)
async def get_adherence_score(
    days: int = Query(30, ge=7, le=365, description="Lookback window in days"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdherenceScoreResponse]:
    """Calculate overall and monthly medication adherence scores and performance tiers."""
    service = MedicineService(db)
    adherence = await service.calculate_adherence_score(current_user.id, days=days)
    return ApiResponse[AdherenceScoreResponse](success=True, message="Adherence score calculated", data=adherence)

@router.get("/medicines/refills", response_model=ApiResponse[RefillAlertResponse], status_code=status.HTTP_200_OK)
async def get_refill_alerts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RefillAlertResponse]:
    """Get list of medications that have reached or dropped below their refill threshold."""
    service = MedicineService(db)
    refills = await service.get_refill_alerts(current_user.id)
    return ApiResponse[RefillAlertResponse](success=True, message="Refill alerts retrieved", data=refills)

@router.patch("/medicines/{medication_id}", response_model=ApiResponse[MedicationResponse], status_code=status.HTTP_200_OK)
async def update_medication(
    medication_id: uuid.UUID,
    req: MedicationUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MedicationResponse]:
    """Update medication details, end date, or inventory count."""
    service = MedicineService(db)
    med = await service.update_medication(current_user.id, medication_id, req)
    payload = MedicationResponse.model_validate(med)
    return ApiResponse[MedicationResponse](success=True, message="Medication updated", data=payload)
