import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    action: str
    resource: str
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PatientActivityItem(BaseModel):
    id: uuid.UUID
    action_label: str
    description: str
    resource_type: str
    ip_address: Optional[str] = None
    timestamp: datetime

class PatientActivitySummaryResponse(BaseModel):
    user_id: uuid.UUID
    total_events: int
    activities: List[PatientActivityItem]

class AdminAuditLogListResponse(BaseModel):
    total_count: int
    limit: int
    offset: int
    logs: List[AuditLogResponse]
