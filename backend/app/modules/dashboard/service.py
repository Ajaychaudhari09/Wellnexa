import uuid
from datetime import datetime, date, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.user import User
from app.models.profile import Profile
from app.models.health import HealthMetric, MetricTypeEnum
from app.models.report import MedicalReport
from app.models.fitness import DailyActivitySummary
from app.modules.medicines.service import MedicineService
from app.modules.reminders.service import ReminderService
from app.modules.nutrition.service import NutritionService
from app.modules.wellness.service import WellnessService
from app.modules.dashboard.schemas import (
    UserProfileHeader,
    MedicineDoseSummary,
    TodayMedicineWidget,
    ReminderSummaryItem,
    TodayReminderWidget,
    VitalsMetricItem,
    VitalsWidget,
    NutritionWidget,
    LatestReportWidget,
    MoodWidget,
    AdherenceWidget,
    QuickActionItem,
    HomeDashboardResponse,
)

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.medicine_service = MedicineService(db)
        self.reminder_service = ReminderService(db)
        self.nutrition_service = NutritionService(db)
        self.wellness_service = WellnessService(db)

    async def get_home_dashboard(self, user_id: uuid.UUID) -> HomeDashboardResponse:
        today = datetime.now(timezone.utc).date()
        hour = datetime.now(timezone.utc).hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        # 1. Profile Header
        prof_res = await self.db.execute(select(Profile).where(Profile.user_id == user_id))
        prof = prof_res.scalar_one_or_none()
        first_name = prof.first_name if prof else "WellNexa"
        last_name = prof.last_name if prof else "User"
        gender = prof.gender.value if prof and prof.gender else None
        blood = prof.blood_group.value if prof and prof.blood_group else None

        header = UserProfileHeader(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            blood_group=blood,
        )

        # 2. Today's Medicine Checklist
        med_sched = await self.medicine_service.get_today_schedule(user_id, today)
        med_doses = [
            MedicineDoseSummary(
                medication_id=d.medication_id,
                name=d.medication_name,
                dosage=d.dosage,
                timing=d.timing,
                time_slot=d.time_slot,
                is_taken=(d.status == "TAKEN"),
            )
            for d in med_sched.doses
        ]
        med_widget = TodayMedicineWidget(
            total_scheduled=med_sched.total_doses,
            taken_count=med_sched.taken_doses,
            pending_count=med_sched.pending_doses,
            doses=med_doses,
        )

        # 3. Today's Reminders
        rem_data = await self.reminder_service.get_today_due_reminders(user_id, today)
        rem_items = [
            ReminderSummaryItem(
                id=r.reminder_id,
                title=r.title,
                due_time=r.due_time,
                reminder_type=r.reminder_type,
                is_completed=(r.status == "COMPLETED"),
            )
            for r in rem_data.reminders[:4]
        ]
        rem_widget = TodayReminderWidget(
            total_due=rem_data.total_due,
            completed_count=rem_data.completed_count,
            upcoming_reminders=rem_items,
        )

        # 4. Key Vitals & BMI
        metric_types_to_fetch = [
            MetricTypeEnum.BLOOD_PRESSURE_SYSTOLIC,
            MetricTypeEnum.BLOOD_PRESSURE_DIASTOLIC,
            MetricTypeEnum.BLOOD_GLUCOSE_FASTING,
            MetricTypeEnum.WEIGHT_KG,
            MetricTypeEnum.BMI,
            MetricTypeEnum.HEART_RATE_BPM,
        ]
        vitals_items: List[VitalsMetricItem] = []
        bmi_val = None
        bmi_cat = None

        for m_type in metric_types_to_fetch:
            q = select(HealthMetric).where(
                and_(HealthMetric.user_id == user_id, HealthMetric.metric_type == m_type)
            ).order_by(desc(HealthMetric.recorded_at)).limit(1)
            res = await self.db.execute(q)
            m = res.scalar_one_or_none()
            if m:
                if m_type == MetricTypeEnum.BMI:
                    bmi_val = m.value
                    if bmi_val < 18.5:
                        bmi_cat = "Underweight"
                    elif bmi_val < 25.0:
                        bmi_cat = "Normal"
                    elif bmi_val < 30.0:
                        bmi_cat = "Overweight"
                    else:
                        bmi_cat = "Obese"
                else:
                    label = m_type.value.replace("_", " ").title()
                    vitals_items.append(
                        VitalsMetricItem(
                            metric_type=m_type.value,
                            label=label,
                            value=m.value,
                            unit=m.unit,
                            status="NORMAL",
                        )
                    )

        vitals_widget = VitalsWidget(
            bmi=bmi_val,
            bmi_category=bmi_cat,
            latest_metrics=vitals_items,
        )

        # 5. Nutrition & Hydration Progress
        nut_summary = await self.nutrition_service.get_daily_summary(user_id, today)
        act_res = await self.db.execute(
            select(DailyActivitySummary).where(
                and_(DailyActivitySummary.user_id == user_id, DailyActivitySummary.date == today)
            )
        )
        act = act_res.scalar_one_or_none()
        water_val = act.water_ml if act else 0

        nutrition_widget = NutritionWidget(
            calories_consumed=nut_summary.total_calories,
            calorie_target=nut_summary.calorie_target,
            remaining_calories=nut_summary.remaining_calories,
            water_ml_consumed=water_val,
            water_ml_target=2500,
            meals_logged_count=nut_summary.meals_logged_count,
        )

        # 6. Latest Medical Report Status
        rep_q = select(MedicalReport).where(MedicalReport.user_id == user_id).order_by(desc(MedicalReport.created_at)).limit(1)
        rep_res = await self.db.execute(rep_q)
        latest_rep = rep_res.scalar_one_or_none()

        if latest_rep:
            exts = latest_rep.extractions
            flagged = sum(1 for e in exts if e.flag_status and e.flag_status.value in ("HIGH", "LOW", "CRITICAL"))
            rep_widget = LatestReportWidget(
                has_reports=True,
                report_id=latest_rep.id,
                report_type=latest_rep.report_type.value,
                status=latest_rep.status.value,
                report_date=latest_rep.report_date or latest_rep.created_at.date(),
                total_parameters_tested=len(exts),
                flagged_count=flagged,
            )
        else:
            rep_widget = LatestReportWidget(has_reports=False)

        # 7. Today's Mood Status
        mood_obj = await self.wellness_service.get_today_mood(user_id)
        mood_widget = MoodWidget(
            is_logged_today=(mood_obj is not None),
            mood_score=mood_obj.mood_score if mood_obj else None,
            primary_emotion=mood_obj.primary_emotion.value if mood_obj else None,
            gratitude_note=mood_obj.gratitude_note if mood_obj else None,
        )

        # 8. Weekly Adherence Card
        adh_score = await self.medicine_service.calculate_adherence_score(user_id, days=30)
        adherence_widget = AdherenceWidget(
            adherence_percentage=adh_score.overall_adherence_percentage,
            tier=adh_score.adherence_tier,
            taken_doses_this_month=adh_score.total_taken,
            total_doses_this_month=adh_score.total_scheduled,
        )

        # 9. Quick Actions
        quick_actions = [
            QuickActionItem(id="log_vitals", label="Log Vitals", icon="heart_pulse", route="/vitals/add"),
            QuickActionItem(id="upload_report", label="Upload Report", icon="document_upload", route="/documents/upload"),
            QuickActionItem(id="log_meal", label="Log Meal", icon="nutrition", route="/nutrition/log"),
            QuickActionItem(id="chat_ai", label="Ask AI", icon="chat_sparkle", route="/assistant"),
            QuickActionItem(id="share_doctor", label="Doctor Share", icon="qr_code", route="/doctor/share"),
        ]

        return HomeDashboardResponse(
            greeting=f"{greeting}, {first_name}!",
            current_date=today,
            profile=header,
            medicines=med_widget,
            reminders=rem_widget,
            vitals=vitals_widget,
            nutrition=nutrition_widget,
            latest_report=rep_widget,
            mood=mood_widget,
            adherence=adherence_widget,
            quick_actions=quick_actions,
        )
