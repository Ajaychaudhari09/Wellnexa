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
    confirmed_items: Optional[List[ConfirmItemPayload]] = Field(default_factory=list)
    report_date: Optional[date] = None
    lab_name: Optional[str] = None
    notes: Optional[str] = None

# ----------------- Explanation & Comparison Schemas -----------------
class FindingItem(BaseModel):
    test_name: str
    value: float
    unit: str
    flag: str
    reference_range: str
    patient_explanation: str

class ReportExplanationResponse(BaseModel):
    report_type: str
    is_ai_generated: bool
    overview: str
    total_parameters_tested: int
    normal_parameters_count: int
    flagged_parameters_count: int
    findings: List[FindingItem]
    lifestyle_context: str
    suggested_questions_for_doctor: List[str]
    medical_disclaimer: str

class ParameterComparisonItem(BaseModel):
    test_name: str
    current_value: float
    previous_value: float
    unit: str
    delta: float
    percentage_change: float
    trend_direction: str # INCREASED, DECREASED, STABLE
    current_flag: str
    previous_flag: str

class HistoricalComparisonResponse(BaseModel):
    current_report_id: uuid.UUID
    previous_report_id: Optional[uuid.UUID] = None
    report_type: str
    has_previous_report: bool
    parameters_compared: List[ParameterComparisonItem]

class ParameterHistoryPoint(BaseModel):
    report_id: uuid.UUID
    report_date: Optional[date] = None
    created_at: datetime
    value: float
    unit: str
    flag_status: str

class ParameterHistoryResponse(BaseModel):
    test_name: str
    unit: str
    data_points: List[ParameterHistoryPoint]
