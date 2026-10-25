import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.modules.appointments.schemas import AppointmentCreateRequest, AppointmentUpdateRequest, AppointmentResponse
from app.modules.appointments.service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointments Management"])

@router.post("", response_model=ApiResponse[AppointmentResponse], status_code=status.HTTP_201_CREATED)
async def create_appointment(
    req: AppointmentCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AppointmentResponse]:
    """Schedule a clinical or telehealth appointment, updating health timeline and reminder schedule."""
    service = AppointmentService(db)
    appointment = await service.create_appointment(current_user.id, req)
    payload = AppointmentResponse.model_validate(appointment)
    return ApiResponse[AppointmentResponse](success=True, message="Appointment successfully scheduled", data=payload)

@router.get("", response_model=ApiResponse[List[AppointmentResponse]], status_code=status.HTTP_200_OK)
async def get_appointments(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[AppointmentResponse]]:
    """Retrieve scheduled and historical appointments for current patient."""
    service = AppointmentService(db)
    appointments = await service.get_user_appointments(current_user.id)
    payload = [AppointmentResponse.model_validate(a) for a in appointments]
    return ApiResponse[List[AppointmentResponse]](success=True, message="Appointments retrieved successfully", data=payload)

@router.patch("/{appointment_id}", response_model=ApiResponse[AppointmentResponse], status_code=status.HTTP_200_OK)
async def update_appointment(
    appointment_id: uuid.UUID,
    req: AppointmentUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AppointmentResponse]:
    """Reschedule or update appointment details."""
    service = AppointmentService(db)
    appointment = await service.update_appointment(current_user.id, appointment_id, req)
    payload = AppointmentResponse.model_validate(appointment)
    return ApiResponse[AppointmentResponse](success=True, message="Appointment updated", data=payload)

@router.delete("/{appointment_id}", response_model=ApiResponse[AppointmentResponse], status_code=status.HTTP_200_OK)
async def cancel_appointment(
    appointment_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AppointmentResponse]:
    """Cancel a scheduled appointment."""
    service = AppointmentService(db)
    appointment = await service.cancel_appointment(current_user.id, appointment_id)
    payload = AppointmentResponse.model_validate(appointment)
    return ApiResponse[AppointmentResponse](success=True, message="Appointment cancelled", data=payload)
