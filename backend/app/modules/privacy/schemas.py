import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class UserConsentUpdateRequest(BaseModel):
    allow_ai_analysis: Optional[bool] = None
    allow_anonymized_insights: Optional[bool] = None
    allow_doctor_sharing: Optional[bool] = None
    data_retention_days: Optional[int] = Field(None, ge=0, le=3650) # 0 to 10 years

class UserConsentResponse(BaseModel):
    user_id: uuid.UUID
    allow_ai_analysis: bool
    allow_anonymized_insights: bool
    allow_doctor_sharing: bool
    data_retention_days: int
    updated_at: datetime

    class Config:
        from_attributes = True

class AccessAuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    actor_id: Optional[uuid.UUID] = None
    actor_role: str
    action: str
    resource: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class HealthDataExportResponse(BaseModel):
    user_id: uuid.UUID
    export_timestamp: datetime
    format_version: str = "1.0"
    profile: Optional[Dict[str, Any]] = None
    health_metrics: List[Dict[str, Any]] = []
    allergies: List[Dict[str, Any]] = []
    conditions: List[Dict[str, Any]] = []
    medications: List[Dict[str, Any]] = []
    nutrition_logs: List[Dict[str, Any]] = []
    workout_logs: List[Dict[str, Any]] = []
    mood_logs: List[Dict[str, Any]] = []
    reports: List[Dict[str, Any]] = []
    timeline_events: List[Dict[str, Any]] = []

class DeleteAccountRequest(BaseModel):
    confirmation_password: str = Field(..., min_length=6)
    reason: Optional[str] = None
