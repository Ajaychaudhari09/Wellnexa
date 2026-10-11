import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class NextActionItem(BaseModel):
    action: str
    reason: str
    category: str

class HealthSnapshotResponse(BaseModel):
    patient_name: str
    is_ai_generated: bool
    overview: str
    positive_trends: List[str]
    areas_for_attention: List[str]
    adherence_overview: str
    suggested_next_actions: List[NextActionItem]
    medical_disclaimer: str
    generated_at: datetime
