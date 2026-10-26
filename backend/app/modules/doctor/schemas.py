import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.doctor import AccessScopeEnum, GrantStatusEnum

# ----------------- Access Grants -----------------
class CreateAccessGrantRequest(BaseModel):
    doctor_email: str = Field(..., min_length=3, max_length=255)
    access_scope: AccessScopeEnum = AccessScopeEnum.FULL_ACCESS
    duration_hours: int = Field(default=24, ge=1, le=720) # 1 hr up to 30 days
    notes: Optional[str] = Field(None, max_length=255)

class AccessGrantResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: Optional[uuid.UUID] = None
    access_token: str
    access_scope: str
    expires_at: datetime
    status: str
    notes: Optional[str] = None
    share_url: str
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Consultations -----------------
class DoctorConsultationCreateRequest(BaseModel):
    doctor_name: str = Field(..., min_length=1, max_length=150)
    clinic_name: Optional[str] = Field(None, max_length=150)
    consultation_date: Optional[date] = None
    chief_complaint: str = Field(..., min_length=1, max_length=300)
    clinical_observations: Optional[str] = None
    recommended_actions: Optional[str] = None
    follow_up_date: Optional[date] = None

class DoctorConsultationResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: Optional[uuid.UUID] = None
    doctor_name: str
    clinic_name: Optional[str] = None
    consultation_date: date
    chief_complaint: str
    clinical_observations: Optional[str] = None
    recommended_actions: Optional[str] = None
    follow_up_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Clinical Summary -----------------
class SharedMedicationItem(BaseModel):
    name: str
    dosage: str
    timing: str
    frequency: str
    instructions: Optional[str] = None

class SharedReportItem(BaseModel):
    id: uuid.UUID
    report_type: str
    status: str
    created_at: datetime
    extractions_summary: List[Dict[str, Any]] = []

class PatientClinicalSummaryResponse(BaseModel):
    patient_id: uuid.UUID
    full_name: str
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: List[str] = []
    chronic_conditions: List[str] = []
    active_medications: List[SharedMedicationItem] = []
    recent_metrics: Dict[str, Any] = {}
    confirmed_reports: List[SharedReportItem] = []
    recent_timeline_events: List[Dict[str, Any]] = []
    access_scope: str
    grant_expires_at: datetime
