import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.core.security import verify_password
from app.core.exceptions import NotFoundException, UnauthorizedException, WellNexaException
from app.models.user import User
from app.models.profile import Profile
from app.models.health import Allergy, MedicalCondition, HealthMetric
from app.models.medicine import Medication
from app.models.nutrition import MealLog
from app.models.fitness import WorkoutLog
from app.models.wellness import MoodLog
from app.models.report import MedicalReport
from app.models.timeline import HealthTimelineEvent
from app.models.privacy import UserConsent, AccessAuditLog
from app.modules.privacy.schemas import (
    UserConsentUpdateRequest,
    HealthDataExportResponse,
)

class PrivacyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ----------------- Consent Controls -----------------
    async def get_or_create_consent(self, user_id: uuid.UUID) -> UserConsent:
        query = select(UserConsent).where(UserConsent.user_id == user_id)
        result = await self.db.execute(query)
        consent = result.scalar_one_or_none()
        if not consent:
            consent = UserConsent(user_id=user_id)
            self.db.add(consent)
            await self.db.flush()
        return consent

    async def update_consent(self, user_id: uuid.UUID, req: UserConsentUpdateRequest) -> UserConsent:
        consent = await self.get_or_create_consent(user_id)
        if req.allow_ai_analysis is not None:
            consent.allow_ai_analysis = req.allow_ai_analysis
        if req.allow_anonymized_insights is not None:
            consent.allow_anonymized_insights = req.allow_anonymized_insights
        if req.allow_doctor_sharing is not None:
            consent.allow_doctor_sharing = req.allow_doctor_sharing
        if req.data_retention_days is not None:
            consent.data_retention_days = req.data_retention_days
        await self.db.flush()
        return consent

    # ----------------- Access Audit Logs -----------------
    async def log_access_event(
        self,
        user_id: uuid.UUID,
        actor_id: Optional[uuid.UUID],
        actor_role: str,
        action: str,
        resource: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AccessAuditLog:
        log = AccessAuditLog(
            user_id=user_id,
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def get_access_audit_logs(self, user_id: uuid.UUID, limit: int = 50) -> List[AccessAuditLog]:
        query = select(AccessAuditLog).where(AccessAuditLog.user_id == user_id).order_by(desc(AccessAuditLog.created_at)).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ----------------- Health Data Export (GDPR / HIPAA Portability) -----------------
    async def export_complete_health_data(
        self, user_id: uuid.UUID, ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> HealthDataExportResponse:
        now = datetime.now(timezone.utc)

        # Profile
        prof_res = await self.db.execute(select(Profile).where(Profile.user_id == user_id))
        prof = prof_res.scalar_one_or_none()
        prof_dict = {
            "first_name": prof.first_name,
            "last_name": prof.last_name,
            "gender": prof.gender.value if prof.gender else None,
            "blood_group": prof.blood_group.value if prof.blood_group else None,
            "date_of_birth": str(prof.date_of_birth) if prof.date_of_birth else None,
            "height_cm": prof.height_cm,
            "weight_kg": prof.weight_kg,
            "emergency_contact": prof.emergency_contact_phone,
        } if prof else None

        # Metrics
        met_res = await self.db.execute(select(HealthMetric).where(HealthMetric.user_id == user_id).order_by(desc(HealthMetric.recorded_at)))
        metrics = [{"type": m.metric_type.value, "value": m.value, "unit": m.unit, "recorded_at": str(m.recorded_at), "source": m.source.value} for m in met_res.scalars().all()]

        # Allergies
        alg_res = await self.db.execute(select(Allergy).where(Allergy.user_id == user_id))
        allergies = [{"allergen": a.allergen, "severity": a.severity.value, "reaction": a.reaction} for a in alg_res.scalars().all()]

        # Conditions
        cond_res = await self.db.execute(select(MedicalCondition).where(MedicalCondition.user_id == user_id))
        conditions = [{"condition": c.condition_name, "status": c.status.value, "diagnosed_date": str(c.diagnosed_date) if c.diagnosed_date else None} for c in cond_res.scalars().all()]

        # Medications
        med_res = await self.db.execute(select(Medication).where(Medication.user_id == user_id))
        meds = [{"name": m.name, "dosage": m.dosage, "timing": m.timing.value, "frequency": m.frequency.value, "is_active": m.is_active} for m in med_res.scalars().all()]

        # Nutrition
        nut_res = await self.db.execute(select(MealLog).where(MealLog.user_id == user_id).order_by(desc(MealLog.logged_date)).limit(100))
        meals = [{"type": m.meal_type.value, "date": str(m.logged_date), "calories": m.total_calories, "protein": m.total_protein, "carbs": m.total_carbs, "fat": m.total_fat} for m in nut_res.scalars().all()]

        # Workouts
        w_res = await self.db.execute(select(WorkoutLog).where(WorkoutLog.user_id == user_id).order_by(desc(WorkoutLog.logged_date)).limit(100))
        workouts = [{"activity": w.activity_type.value, "title": w.title, "duration": w.duration_minutes, "calories": w.calories_burned, "date": str(w.logged_date)} for w in w_res.scalars().all()]

        # Mood
        mood_res = await self.db.execute(select(MoodLog).where(MoodLog.user_id == user_id).order_by(desc(MoodLog.logged_date)).limit(100))
        moods = [{"score": mo.mood_score, "emotion": mo.primary_emotion.value, "date": str(mo.logged_date), "journal": mo.journal_text} for mo in mood_res.scalars().all()]

        # Reports
        rep_res = await self.db.execute(select(MedicalReport).where(MedicalReport.user_id == user_id).order_by(desc(MedicalReport.created_at)))
        reports = [{"report_type": r.report_type.value, "status": r.status.value, "lab": r.lab_name, "date": str(r.created_at)} for r in rep_res.scalars().all()]

        # Timeline
        t_res = await self.db.execute(select(HealthTimelineEvent).where(HealthTimelineEvent.user_id == user_id).order_by(desc(HealthTimelineEvent.occurred_at)).limit(100))
        timeline = [{"title": e.title, "category": e.category.value, "summary": e.summary, "occurred_at": str(e.occurred_at)} for e in t_res.scalars().all()]

        # Log Access Audit Event
        await self.log_access_event(
            user_id=user_id,
            actor_id=user_id,
            actor_role="PATIENT",
            action="EXPORT_HEALTH_DATA",
            resource="complete_health_record",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return HealthDataExportResponse(
            user_id=user_id,
            export_timestamp=now,
            profile=prof_dict,
            health_metrics=metrics,
            allergies=allergies,
            conditions=conditions,
            medications=meds,
            nutrition_logs=meals,
            workout_logs=workouts,
            mood_logs=moods,
            reports=reports,
            timeline_events=timeline,
        )

    # ----------------- Account Deletion -----------------
    async def delete_user_account_and_data(self, user_id: uuid.UUID, confirmation_password: str) -> None:
        user_res = await self.db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        if not user:
            raise NotFoundException("User", user_id)

        if not verify_password(confirmation_password, user.hashed_password):
            raise UnauthorizedException("Incorrect confirmation password")

        # Delete user (CASCADE deletes profile, documents, metrics, logs, timeline)
        await self.db.delete(user)
        await self.db.flush()
