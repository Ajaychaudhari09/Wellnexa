import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.profile import Profile
from app.models.health import HealthMetric, MetricTypeEnum
from app.models.report import MedicalReport, ExtractionStatusEnum
from app.modules.medicines.service import MedicineService
from app.modules.nutrition.service import NutritionService
from app.modules.fitness.service import FitnessService
from app.modules.wellness.service import WellnessService
from ai.snapshot.health_snapshot import HealthSnapshotEngine
from app.modules.snapshot.schemas import HealthSnapshotResponse, NextActionItem

class SnapshotService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.medicine_service = MedicineService(db)
        self.nutrition_service = NutritionService(db)
        self.fitness_service = FitnessService(db)
        self.wellness_service = WellnessService(db)

    async def get_health_snapshot(self, user_id: uuid.UUID) -> HealthSnapshotResponse:
        now = datetime.now(timezone.utc)

        # 1. Profile
        prof_res = await self.db.execute(select(Profile).where(Profile.user_id == user_id))
        prof = prof_res.scalar_one_or_none()
        profile_data = {
            "first_name": prof.first_name if prof else "Patient",
            "gender": prof.gender.value if prof and prof.gender else None,
        }

        # 2. Vitals & BMI
        bmi_res = await self.db.execute(
            select(HealthMetric).where(
                and_(HealthMetric.user_id == user_id, HealthMetric.metric_type == MetricTypeEnum.BMI)
            ).order_by(desc(HealthMetric.recorded_at)).limit(1)
        )
        bmi_metric = bmi_res.scalar_one_or_none()
        bmi_val = bmi_metric.value if bmi_metric else None
        bmi_cat = "Normal"
        if bmi_val:
            if bmi_val < 18.5:
                bmi_cat = "Underweight"
            elif bmi_val < 25.0:
                bmi_cat = "Normal"
            elif bmi_val < 30.0:
                bmi_cat = "Overweight"
            else:
                bmi_cat = "Obese"

        vitals_data = {"bmi": bmi_val, "bmi_category": bmi_cat}

        # 3. Adherence
        adh_score = await self.medicine_service.calculate_adherence_score(user_id, days=30)
        adherence_data = {
            "overall_adherence_percentage": adh_score.overall_adherence_percentage,
            "adherence_tier": adh_score.adherence_tier,
            "total_taken": adh_score.total_taken,
            "total_scheduled": adh_score.total_scheduled,
        }

        # 4. Nutrition
        nut_summary = await self.nutrition_service.get_daily_summary(user_id)
        nutrition_data = {
            "calories_consumed": nut_summary.total_calories,
            "calorie_target": nut_summary.calorie_target,
            "water_ml_consumed": 2200, # Estimated default baseline
        }

        # 5. Fitness
        fitness_trends = await self.fitness_service.get_fitness_trends(user_id, days=7)
        fitness_data = {
            "average_daily_steps": fitness_trends.average_daily_steps,
            "average_sleep_hours": fitness_trends.average_sleep_hours,
            "average_active_minutes": fitness_trends.average_active_minutes,
        }

        # 6. Mood
        mood_trends = await self.wellness_service.get_weekly_mood_trends(user_id, days=7)
        mood_data = {
            "average_mood_score": mood_trends.average_mood_score,
            "predominant_emotion": mood_trends.predominant_emotion,
        }

        # 7. Reports
        rep_res = await self.db.execute(
            select(MedicalReport).where(
                and_(MedicalReport.user_id == user_id, MedicalReport.status == ExtractionStatusEnum.CONFIRMED)
            ).order_by(desc(MedicalReport.created_at)).limit(5)
        )
        reports_data = [
            {
                "report_type": r.report_type.value,
                "extractions": [
                    {"test_name": e.test_name, "value": e.confirmed_value or e.detected_value, "flag_status": e.flag_status.value}
                    for e in r.extractions
                ]
            }
            for r in rep_res.scalars().all()
        ]

        # 8. Synthesize
        raw_snapshot = HealthSnapshotEngine.generate_snapshot(
            profile_data=profile_data,
            vitals_data=vitals_data,
            adherence_data=adherence_data,
            nutrition_data=nutrition_data,
            fitness_data=fitness_data,
            mood_data=mood_data,
            reports_data=reports_data,
        )

        return HealthSnapshotResponse(
            patient_name=raw_snapshot["patient_name"],
            is_ai_generated=raw_snapshot["is_ai_generated"],
            overview=raw_snapshot["overview"],
            positive_trends=raw_snapshot["positive_trends"],
            areas_for_attention=raw_snapshot["areas_for_attention"],
            adherence_overview=raw_snapshot["adherence_overview"],
            suggested_next_actions=[NextActionItem(**a) for a in raw_snapshot["suggested_next_actions"]],
            medical_disclaimer=raw_snapshot["medical_disclaimer"],
            generated_at=now,
        )
