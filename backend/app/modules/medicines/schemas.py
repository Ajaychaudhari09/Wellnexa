import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.medicine import MedicationFormEnum, FrequencyEnum, TimingEnum, DoseStatusEnum

# ----------------- Schedules -----------------
class MedicationScheduleItem(BaseModel):
    time_slot: str = Field(..., description="e.g. '09:00', '21:00'")
    dosage_quantity: float = Field(default=1.0, gt=0)
    days_of_week: Optional[str] = "DAILY"

class ScheduleResponse(BaseModel):
    id: uuid.UUID
    time_slot: str
    dosage_quantity: float
    days_of_week: str

    class Config:
        from_attributes = True

# ----------------- Prescriptions -----------------
class PrescriptionCreateRequest(BaseModel):
    document_id: Optional[uuid.UUID] = None
    doctor_name: Optional[str] = Field(None, max_length=150)
    clinic_name: Optional[str] = Field(None, max_length=150)
    prescribed_date: Optional[date] = None
    diagnosis_notes: Optional[str] = Field(None, max_length=500)

class PrescriptionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    document_id: Optional[uuid.UUID] = None
    doctor_name: Optional[str] = None
    clinic_name: Optional[str] = None
    prescribed_date: date
    diagnosis_notes: Optional[str] = None
    medications_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Medications -----------------
class MedicationCreateRequest(BaseModel):
    prescription_id: Optional[uuid.UUID] = None
    name: str = Field(..., min_length=1, max_length=150)
    dosage: str = Field(..., min_length=1, max_length=100) # e.g. "500 mg"
    form: MedicationFormEnum = MedicationFormEnum.TABLET
    frequency: FrequencyEnum = FrequencyEnum.ONCE_DAILY
    timing: TimingEnum = TimingEnum.AFTER_MEAL
    instructions: Optional[str] = Field(None, max_length=300)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    current_stock: int = Field(default=30, ge=0)
    refill_threshold: int = Field(default=5, ge=0)
    schedules: List[MedicationScheduleItem] = []

class MedicationUpdateRequest(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    form: Optional[MedicationFormEnum] = None
    frequency: Optional[FrequencyEnum] = None
    timing: Optional[TimingEnum] = None
    instructions: Optional[str] = None
    end_date: Optional[date] = None
    current_stock: Optional[int] = None
    refill_threshold: Optional[int] = None
    is_active: Optional[bool] = None

class MedicationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    prescription_id: Optional[uuid.UUID] = None
    name: str
    dosage: str
    form: str
    frequency: str
    timing: str
    instructions: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    current_stock: int
    refill_threshold: int
    is_active: bool
    schedules: List[ScheduleResponse] = []

    class Config:
        from_attributes = True

# ----------------- Dose Logging -----------------
class LogDoseRequest(BaseModel):
    status: DoseStatusEnum = DoseStatusEnum.TAKEN
    scheduled_at: Optional[datetime] = None
    taken_at: Optional[datetime] = None
    notes: Optional[str] = None

class MedicationLogResponse(BaseModel):
    id: uuid.UUID
    medication_id: uuid.UUID
    user_id: uuid.UUID
    scheduled_at: datetime
    status: str
    taken_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# ----------------- Today Schedule -----------------
class TodayDoseItem(BaseModel):
    medication_id: uuid.UUID
    medication_name: str
    dosage: str
    timing: str
    time_slot: str
    status: str # SCHEDULED, TAKEN, MISSED, SKIPPED
    log_id: Optional[uuid.UUID] = None

class TodayMedicationScheduleResponse(BaseModel):
    date: date
    total_doses: int
    taken_doses: int
    pending_doses: int
    doses: List[TodayDoseItem]

# ----------------- Adherence Scoring -----------------
class MonthlyAdherenceItem(BaseModel):
    month_label: str # e.g. "Aug 2026"
    scheduled_count: int
    taken_count: int
    missed_count: int
    adherence_percentage: float

class AdherenceScoreResponse(BaseModel):
    total_scheduled: int
    total_taken: int
    total_missed: int
    overall_adherence_percentage: float
    adherence_tier: str # EXCELLENT, GOOD, NEEDS_ATTENTION
    monthly_history: List[MonthlyAdherenceItem]

# ----------------- Refill Alerts -----------------
class RefillAlertItem(BaseModel):
    medication_id: uuid.UUID
    medication_name: str
    dosage: str
    current_stock: int
    refill_threshold: int
    days_supply_remaining: Optional[int] = None
    refill_urgency: str # URGENT, WARNING, ADEQUATE

class RefillAlertResponse(BaseModel):
    total_alerts: int
    medications_requiring_refill: List[RefillAlertItem]
