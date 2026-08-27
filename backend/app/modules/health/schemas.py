import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.health import (
    MetricTypeEnum,
    MetricSourceEnum,
    AllergySeverityEnum,
    ConditionStatusEnum,
    GoalStatusEnum,
)

# ----------------- Health Status -----------------
class HealthStatus(BaseModel):
    status: str = Field(..., description="Overall system status")
    environment: str = Field(..., description="Active environment name")
    version: str = Field(..., description="Backend release version")
    timestamp: datetime = Field(..., description="Current server time (UTC)")
    database: str = Field(..., description="Database connectivity status")

# ----------------- Health Metrics -----------------
class MetricCreateItem(BaseModel):
    metric_type: MetricTypeEnum
    value: float
    unit: str
    recorded_at: Optional[datetime] = None
    source: MetricSourceEnum = MetricSourceEnum.MANUAL
    notes: Optional[str] = None
    metadata_info: Optional[Dict[str, Any]] = None

class MetricBatchCreateRequest(BaseModel):
    metrics: List[MetricCreateItem]

class MetricResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    metric_type: str
    value: float
    unit: str
    recorded_at: datetime
    source: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class MetricTrendPoint(BaseModel):
    timestamp: datetime
    value: float
    unit: str

class MetricTrendResponse(BaseModel):
    metric_type: str
    unit: str
    latest_value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    avg_value: Optional[float] = None
    data_points: List[MetricTrendPoint]

# ----------------- Allergies -----------------
class AllergyCreateRequest(BaseModel):
    allergen: str = Field(..., min_length=1, max_length=150)
    reaction: Optional[str] = Field(None, max_length=255)
    severity: AllergySeverityEnum = AllergySeverityEnum.MODERATE
    is_active: bool = True

class AllergyResponse(BaseModel):
    id: uuid.UUID
    allergen: str
    reaction: Optional[str] = None
    severity: str
    is_active: bool

    class Config:
        from_attributes = True

# ----------------- Medical Conditions -----------------
class ConditionCreateRequest(BaseModel):
    condition_name: str = Field(..., min_length=1, max_length=150)
    diagnosed_date: Optional[date] = None
    status: ConditionStatusEnum = ConditionStatusEnum.ACTIVE
    notes: Optional[str] = None

class ConditionResponse(BaseModel):
    id: uuid.UUID
    condition_name: str
    diagnosed_date: Optional[date] = None
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# ----------------- Health Goals -----------------
class GoalCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    goal_type: str = Field(..., description="e.g. WEIGHT_LOSS, BLOOD_SUGAR_CONTROL")
    target_value: float
    current_value: Optional[float] = None
    unit: str
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    status: GoalStatusEnum = GoalStatusEnum.IN_PROGRESS
    notes: Optional[str] = None

class GoalResponse(BaseModel):
    id: uuid.UUID
    title: str
    goal_type: str
    target_value: float
    current_value: Optional[float] = None
    unit: str
    start_date: date
    target_date: Optional[date] = None
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# ----------------- Lifestyle Profile -----------------
class LifestyleUpdateRequest(BaseModel):
    diet_type: Optional[str] = "OMNIVORE"
    activity_level: Optional[str] = "MODERATE"
    smoking_status: Optional[str] = "NON_SMOKER"
    alcohol_status: Optional[str] = "OCCASIONAL"
    sleep_target_hours: Optional[float] = 8.0
    water_target_liters: Optional[float] = 2.5

class LifestyleResponse(BaseModel):
    diet_type: str
    activity_level: str
    smoking_status: str
    alcohol_status: str
    sleep_target_hours: float
    water_target_liters: float

    class Config:
        from_attributes = True

# ----------------- Unified Health Summary -----------------
class UnifiedHealthSummaryResponse(BaseModel):
    bmi: Optional[MetricResponse] = None
    latest_weight: Optional[MetricResponse] = None
    latest_height: Optional[MetricResponse] = None
    latest_bp_systolic: Optional[MetricResponse] = None
    latest_bp_diastolic: Optional[MetricResponse] = None
    latest_blood_glucose: Optional[MetricResponse] = None
    active_allergies: List[AllergyResponse] = []
    active_conditions: List[ConditionResponse] = []
    active_goals: List[GoalResponse] = []
    lifestyle: Optional[LifestyleResponse] = None
