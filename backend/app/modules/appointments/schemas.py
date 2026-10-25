import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.appointment import AppointmentStatusEnum, AppointmentTypeEnum

class AppointmentCreateRequest(BaseModel):
    doctor_name: str = Field(..., min_length=2, max_length=150)
    specialty: str = Field("General Medicine", max_length=100)
    clinic_or_hospital: Optional[str] = Field(None, max_length=150)
    location: Optional[str] = Field(None, max_length=255)
    appointment_date: date
    appointment_time: str = Field("10:00", max_length=20)
    purpose: str = Field(..., min_length=3, max_length=300)
    notes: Optional[str] = None
    appointment_type: AppointmentTypeEnum = AppointmentTypeEnum.IN_PERSON

class AppointmentUpdateRequest(BaseModel):
    doctor_name: Optional[str] = None
    specialty: Optional[str] = None
    clinic_or_hospital: Optional[str] = None
    location: Optional[str] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[str] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[AppointmentStatusEnum] = None
    appointment_type: Optional[AppointmentTypeEnum] = None

class AppointmentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    doctor_id: Optional[uuid.UUID] = None
    doctor_name: str
    specialty: str
    clinic_or_hospital: Optional[str] = None
    location: Optional[str] = None
    appointment_date: date
    appointment_time: str
    purpose: str
    notes: Optional[str] = None
    status: AppointmentStatusEnum
    appointment_type: AppointmentTypeEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
