import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.report import ReportTypeEnum, ExtractionStatusEnum, FlagStatusEnum

class ExtractionItemResponse(BaseModel):
    id: uuid.UUID
    test_name: str
    metric_type: Optional[str] = None
    detected_value: float
    confirmed_value: Optional[float] = None
    unit: str
    reference_range_low: Optional[float] = None
    reference_range_high: Optional[float] = None
    flag_status: str
    is_confirmed: bool
    user_corrected: bool

    class Config:
        from_attributes = True

class ReportResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    document_id: uuid.UUID
    report_type: str
    report_date: Optional[date] = None
    lab_name: Optional[str] = None
    status: str
    raw_text: Optional[str] = None
    summary_notes: Optional[str] = None
    extractions: List[ExtractionItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

class ConfirmItemPayload(BaseModel):
    extraction_id: uuid.UUID
    confirmed_value: float
    is_confirmed: bool = True

class ConfirmReportRequest(BaseModel):
    confirmed_items: List[ConfirmItemPayload]
    report_date: Optional[date] = None
    lab_name: Optional[str] = None
    notes: Optional[str] = None
