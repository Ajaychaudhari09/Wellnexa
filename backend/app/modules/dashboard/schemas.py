import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class UserProfileHeader(BaseModel):
    user_id: uuid.UUID
    first_name: str
    last_name: str
    gender: Optional[str] = None
    blood_group: Optional[str] = None

class MedicineDoseSummary(BaseModel):
    medication_id: uuid.UUID
    name: str
    dosage: str
    timing: str
    time_slot: str
    is_taken: bool

class TodayMedicineWidget(BaseModel):
    total_scheduled: int
    taken_count: int
    pending_count: int
    doses: List[MedicineDoseSummary] = []

class ReminderSummaryItem(BaseModel):
    id: uuid.UUID
    title: str
    due_time: str
    reminder_type: str
    is_completed: bool

class TodayReminderWidget(BaseModel):
    total_due: int
    completed_count: int
    upcoming_reminders: List[ReminderSummaryItem] = []

class VitalsMetricItem(BaseModel):
    metric_type: str
    label: str
    value: float
    unit: str
    status: Optional[str] = None # NORMAL, HIGH, LOW

class VitalsWidget(BaseModel):
    bmi: Optional[float] = None
    bmi_category: Optional[str] = None
    latest_metrics: List[VitalsMetricItem] = []

class NutritionWidget(BaseModel):
    calories_consumed: float
    calorie_target: float
    remaining_calories: float
    water_ml_consumed: int
    water_ml_target: int
    meals_logged_count: int

class LatestReportWidget(BaseModel):
    has_reports: bool
    report_id: Optional[uuid.UUID] = None
    report_type: Optional[str] = None
    status: Optional[str] = None
    report_date: Optional[date] = None
    total_parameters_tested: Optional[int] = None
    flagged_count: Optional[int] = None

class MoodWidget(BaseModel):
    is_logged_today: bool
    mood_score: Optional[int] = None
    primary_emotion: Optional[str] = None
    gratitude_note: Optional[str] = None

class AdherenceWidget(BaseModel):
    adherence_percentage: float
    tier: str # EXCELLENT, GOOD, NEEDS_ATTENTION
    taken_doses_this_month: int
    total_doses_this_month: int

class QuickActionItem(BaseModel):
    id: str
    label: str
    icon: str
    route: str

class HomeDashboardResponse(BaseModel):
    greeting: str
    current_date: date
    profile: UserProfileHeader
    medicines: TodayMedicineWidget
    reminders: TodayReminderWidget
    vitals: VitalsWidget
    nutrition: NutritionWidget
    latest_report: LatestReportWidget
    mood: MoodWidget
    adherence: AdherenceWidget
    quick_actions: List[QuickActionItem]
