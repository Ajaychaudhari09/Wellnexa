from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin
from app.models.user import User, Role, RoleEnum, user_roles
from app.models.token import RefreshToken
from app.models.profile import Profile, GenderEnum, BloodGroupEnum
from app.models.audit import AuditLog
from app.models.health import (
    HealthMetric,
    MetricTypeEnum,
    MetricSourceEnum,
    Allergy,
    AllergySeverityEnum,
    MedicalCondition,
    ConditionStatusEnum,
    HealthGoal,
    GoalStatusEnum,
    LifestyleProfile,
)
from app.models.timeline import (
    HealthTimelineEvent,
    TimelineCategoryEnum,
    TimelineEventTypeEnum,
)
from app.models.document import (
    MedicalDocument,
    DocumentCategoryEnum,
    DocumentStatusEnum,
)
from app.models.report import (
    MedicalReport,
    ReportExtractionItem,
    ReportTypeEnum,
    ExtractionStatusEnum,
    FlagStatusEnum,
)
from app.models.medicine import (
    Prescription,
    Medication,
    MedicationSchedule,
    MedicationLog,
    MedicationFormEnum,
    FrequencyEnum,
    TimingEnum,
    DoseStatusEnum,
)
from app.models.reminder import (
    Reminder,
    ReminderLog,
    NotificationPreference,
    ReminderTypeEnum,
    RecurrenceTypeEnum,
    ReminderStatusEnum,
)
from app.models.nutrition import (
    FoodItem,
    MealLog,
    MealLogItem,
    NutritionTarget,
    MealPlan,
    GroceryList,
    MealTypeEnum,
    DietTypeEnum,
)
from app.models.fitness import (
    WorkoutLog,
    DailyActivitySummary,
    Habit,
    HabitLog,
    ActivityTypeEnum,
    WorkoutIntensityEnum,
)
from app.models.wellness import (
    MoodLog,
    EmotionEnum,
)
from app.models.chat import (
    ChatSession,
    ChatMessage,
    ChatRoleEnum,
)
from app.models.doctor import (
    PatientAccessGrant,
    DoctorConsultation,
    AccessScopeEnum,
    GrantStatusEnum,
)
from app.models.privacy import (
    UserConsent,
    AccessAuditLog,
)
from app.models.notification import (
    Notification,
    NotificationTypeEnum,
    NotificationPriorityEnum,
)

__all__ = [
    "Base",
    "UUIDMixin",
    "TimestampMixin",
    "User",
    "Role",
    "RoleEnum",
    "user_roles",
    "RefreshToken",
    "Profile",
    "GenderEnum",
    "BloodGroupEnum",
    "AuditLog",
    "HealthMetric",
    "MetricTypeEnum",
    "MetricSourceEnum",
    "Allergy",
    "AllergySeverityEnum",
    "MedicalCondition",
    "ConditionStatusEnum",
    "HealthGoal",
    "GoalStatusEnum",
    "LifestyleProfile",
    "HealthTimelineEvent",
    "TimelineCategoryEnum",
    "TimelineEventTypeEnum",
    "MedicalDocument",
    "DocumentCategoryEnum",
    "DocumentStatusEnum",
    "MedicalReport",
    "ReportExtractionItem",
    "ReportTypeEnum",
    "ExtractionStatusEnum",
    "FlagStatusEnum",
    "Prescription",
    "Medication",
    "MedicationSchedule",
    "MedicationLog",
    "MedicationFormEnum",
    "FrequencyEnum",
    "TimingEnum",
    "DoseStatusEnum",
    "Reminder",
    "ReminderLog",
    "NotificationPreference",
    "ReminderTypeEnum",
    "RecurrenceTypeEnum",
    "ReminderStatusEnum",
    "FoodItem",
    "MealLog",
    "MealLogItem",
    "NutritionTarget",
    "MealPlan",
    "GroceryList",
    "MealTypeEnum",
    "DietTypeEnum",
    "WorkoutLog",
    "DailyActivitySummary",
    "Habit",
    "HabitLog",
    "ActivityTypeEnum",
    "WorkoutIntensityEnum",
    "MoodLog",
    "EmotionEnum",
    "ChatSession",
    "ChatMessage",
    "ChatRoleEnum",
    "PatientAccessGrant",
    "DoctorConsultation",
    "AccessScopeEnum",
    "GrantStatusEnum",
    "UserConsent",
    "AccessAuditLog",
    "Notification",
    "NotificationTypeEnum",
    "NotificationPriorityEnum",
]
