"""Seed realistic demonstration data for MCA project evaluation."""

import asyncio
import secrets
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, Role, RoleEnum, user_roles
from app.models.profile import Profile, GenderEnum, BloodGroupEnum
from app.models.health import (
    HealthMetric, MetricTypeEnum, MetricSourceEnum,
    Allergy, AllergySeverityEnum,
    MedicalCondition, ConditionStatusEnum,
    HealthGoal, GoalStatusEnum,
    LifestyleProfile
)
from app.models.timeline import HealthTimelineEvent, TimelineCategoryEnum, TimelineEventTypeEnum
from app.models.document import MedicalDocument, DocumentCategoryEnum, DocumentStatusEnum
from app.models.report import MedicalReport, ReportExtractionItem, ReportTypeEnum, ExtractionStatusEnum, FlagStatusEnum
from app.models.medicine import (
    Medication, MedicationLog, MedicationSchedule,
    MedicationFormEnum, FrequencyEnum, TimingEnum, DoseStatusEnum
)
from app.models.reminder import (
    Reminder, NotificationPreference, ReminderTypeEnum, RecurrenceTypeEnum, ReminderStatusEnum
)
from app.models.nutrition import MealLog, MealLogItem, NutritionTarget, MealTypeEnum
from app.models.fitness import WorkoutLog, DailyActivitySummary, Habit, ActivityTypeEnum, WorkoutIntensityEnum
from app.models.wellness import MoodLog, EmotionEnum
from app.models.doctor import PatientAccessGrant, DoctorConsultation, AccessScopeEnum, GrantStatusEnum
from app.models.privacy import UserConsent
import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.models.notification import Notification, NotificationTypeEnum, NotificationPriorityEnum

async def seed_all():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
    from app.core.database import Base
    import app.models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_factory() as db:
        print("[WellNexa AI] Seeding realistic demonstration data for project evaluation...")

        # 1. Roles
        roles_dict = {}
        for r_enum in RoleEnum:
            q = select(Role).where(Role.name == r_enum)
            res = await db.execute(q)
            role_obj = res.scalar_one_or_none()
            if not role_obj:
                role_obj = Role(name=r_enum, description=f"{r_enum.value} Role")
                db.add(role_obj)
                await db.flush()
            roles_dict[r_enum] = role_obj

        # 2. Patient User: patient@wellnexa.ai
        patient_q = select(User).where(User.email == "patient@wellnexa.ai")
        patient_res = await db.execute(patient_q)
        patient = patient_res.scalar_one_or_none()

        if not patient:
            patient = User(
                email="patient@wellnexa.ai",
                hashed_password=get_password_hash("Password123!"),
                is_active=True,
                is_verified=True,
            )
            patient.roles.append(roles_dict[RoleEnum.PATIENT])
            db.add(patient)
            await db.flush()

            # Profile
            profile = Profile(
                user_id=patient.id,
                first_name="Bruce",
                last_name="Wayne",
                date_of_birth=date(1990, 5, 19),
                gender=GenderEnum.MALE,
                blood_group=BloodGroupEnum.O_POSITIVE,
                emergency_contact_name="Alfred Pennyworth",
                emergency_contact_phone="+1-555-0199",
            )
            db.add(profile)

            # Consent & Preferences
            consent = UserConsent(
                user_id=patient.id,
                allow_ai_analysis=True,
                allow_anonymized_insights=True,
                allow_doctor_sharing=True,
                data_retention_days=365,
            )
            db.add(consent)

            notif_pref = NotificationPreference(
                user_id=patient.id,
                enable_push=True,
                enable_email=True,
                medicine_alerts=True,
                refill_alerts=True,
            )
            db.add(notif_pref)
            await db.flush()

            # Allergies & Conditions
            allergy = Allergy(user_id=patient.id, allergen="Penicillin", severity=AllergySeverityEnum.HIGH, reaction="Anaphylaxis hives")
            condition = MedicalCondition(user_id=patient.id, condition_name="Mild Primary Hypertension", status=ConditionStatusEnum.ACTIVE, diagnosed_date=date(2023, 3, 15))
            goal = HealthGoal(user_id=patient.id, title="Cardiovascular Endurance", goal_type="STEPS_DAILY", target_value=10000.0, current_value=8500.0, unit="steps", status=GoalStatusEnum.IN_PROGRESS)
            db.add_all([allergy, condition, goal])

            # Vitals
            now = datetime.now(timezone.utc)
            vitals = [
                HealthMetric(user_id=patient.id, metric_type=MetricTypeEnum.HEIGHT_CM, value=188.0, unit="cm", recorded_at=now),
                HealthMetric(user_id=patient.id, metric_type=MetricTypeEnum.WEIGHT_KG, value=85.0, unit="kg", recorded_at=now),
                HealthMetric(user_id=patient.id, metric_type=MetricTypeEnum.BMI, value=24.05, unit="kg/m²", recorded_at=now),
                HealthMetric(user_id=patient.id, metric_type=MetricTypeEnum.BLOOD_PRESSURE_SYSTOLIC, value=118.0, unit="mmHg", recorded_at=now),
                HealthMetric(user_id=patient.id, metric_type=MetricTypeEnum.BLOOD_PRESSURE_DIASTOLIC, value=78.0, unit="mmHg", recorded_at=now),
                HealthMetric(user_id=patient.id, metric_type=MetricTypeEnum.BLOOD_GLUCOSE_FASTING, value=92.0, unit="mg/dL", recorded_at=now),
                HealthMetric(user_id=patient.id, metric_type=MetricTypeEnum.HEART_RATE_BPM, value=64.0, unit="bpm", recorded_at=now),
            ]
            db.add_all(vitals)

            # Document & Confirmed Medical Lab Report
            doc = MedicalDocument(
                user_id=patient.id,
                category=DocumentCategoryEnum.MEDICAL_REPORT,
                status=DocumentStatusEnum.EXTRACTED,
                title="Annual Lipid Profile 2026",
                file_name="annual_lipid_panel.pdf",
                original_file_name="annual_lipid_panel.pdf",
                file_size_bytes=24580,
                mime_type="application/pdf",
                file_path="demo/annual_lipid_panel.pdf",
                checksum_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            )
            db.add(doc)
            await db.flush()

            report = MedicalReport(
                user_id=patient.id,
                document_id=doc.id,
                report_type=ReportTypeEnum.LIPID_PROFILE,
                status=ExtractionStatusEnum.CONFIRMED,
                lab_name="Gotham Metropolitan Diagnostics",
                report_date=date.today() - timedelta(days=5),
            )
            db.add(report)
            await db.flush()

            ext1 = ReportExtractionItem(report_id=report.id, test_name="Total Cholesterol", metric_type=MetricTypeEnum.CHOLESTEROL_TOTAL, detected_value=195.0, confirmed_value=195.0, unit="mg/dL", reference_range_low=0.0, reference_range_high=200.0, flag_status=FlagStatusEnum.NORMAL, is_confirmed=True)
            ext2 = ReportExtractionItem(report_id=report.id, test_name="HDL Cholesterol", metric_type=MetricTypeEnum.CHOLESTEROL_HDL, detected_value=58.0, confirmed_value=58.0, unit="mg/dL", reference_range_low=40.0, reference_range_high=60.0, flag_status=FlagStatusEnum.NORMAL, is_confirmed=True)
            ext3 = ReportExtractionItem(report_id=report.id, test_name="LDL Cholesterol", metric_type=MetricTypeEnum.CHOLESTEROL_LDL, detected_value=112.0, confirmed_value=112.0, unit="mg/dL", reference_range_low=0.0, reference_range_high=100.0, flag_status=FlagStatusEnum.HIGH, is_confirmed=True)
            ext4 = ReportExtractionItem(report_id=report.id, test_name="Triglycerides", metric_type=MetricTypeEnum.TRIGLYCERIDES, detected_value=125.0, confirmed_value=125.0, unit="mg/dL", reference_range_low=0.0, reference_range_high=150.0, flag_status=FlagStatusEnum.NORMAL, is_confirmed=True)
            db.add_all([ext1, ext2, ext3, ext4])

            # Prescriptions & Medicines
            med1 = Medication(user_id=patient.id, name="Metformin", dosage="500 mg", form=MedicationFormEnum.TABLET, frequency=FrequencyEnum.TWICE_DAILY, timing=TimingEnum.AFTER_MEAL, current_stock=45, refill_threshold=10, is_active=True)
            med2 = Medication(user_id=patient.id, name="Omega-3 Fish Oil", dosage="1000 mg", form=MedicationFormEnum.CAPSULE, frequency=FrequencyEnum.ONCE_DAILY, timing=TimingEnum.AFTER_MEAL, current_stock=28, refill_threshold=7, is_active=True)
            med3 = Medication(user_id=patient.id, name="Vitamin D3", dosage="1000 IU", form=MedicationFormEnum.TABLET, frequency=FrequencyEnum.ONCE_DAILY, timing=TimingEnum.BEFORE_MEAL, current_stock=60, refill_threshold=14, is_active=True)
            db.add_all([med1, med2, med3])
            await db.flush()

            # Dose Logs (High adherence ~93%)
            for i in range(14):
                log_day = now - timedelta(days=i)
                db.add(MedicationLog(medication_id=med1.id, user_id=patient.id, scheduled_at=log_day, taken_at=log_day, status=DoseStatusEnum.TAKEN))
                db.add(MedicationLog(medication_id=med2.id, user_id=patient.id, scheduled_at=log_day, taken_at=log_day if i != 3 else None, status=DoseStatusEnum.TAKEN if i != 3 else DoseStatusEnum.MISSED))

            # Smart Reminders
            r1 = Reminder(user_id=patient.id, reminder_type=ReminderTypeEnum.MEDICINE, title="Take Metformin (500mg)", due_time="08:30", recurrence=RecurrenceTypeEnum.DAILY)
            r2 = Reminder(user_id=patient.id, reminder_type=ReminderTypeEnum.WATER, title="Hydration Break (500ml)", due_time="11:00", recurrence=RecurrenceTypeEnum.DAILY)
            r3 = Reminder(user_id=patient.id, reminder_type=ReminderTypeEnum.MEDICINE, title="Take Metformin & Omega-3", due_time="20:00", recurrence=RecurrenceTypeEnum.DAILY)
            db.add_all([r1, r2, r3])

            # Nutrition Meals
            meal1 = MealLog(user_id=patient.id, meal_type=MealTypeEnum.BREAKFAST, total_calories=420.0, total_protein=24.0, total_carbs=52.0, total_fat=12.0, logged_date=date.today())
            db.add(meal1)
            await db.flush()
            item1 = MealLogItem(meal_log_id=meal1.id, food_name="Rolled Oats with Almond Milk & Blueberries", serving_quantity=1.0, calories_kcal=320.0, protein_g=12.0, carbs_g=48.0, fat_g=6.0)
            item2 = MealLogItem(meal_log_id=meal1.id, food_name="Boiled Egg Whites (x3)", serving_quantity=3.0, calories_kcal=100.0, protein_g=12.0, carbs_g=4.0, fat_g=6.0)
            db.add_all([item1, item2])

            # Workouts & Daily Activity
            workout = WorkoutLog(user_id=patient.id, activity_type=ActivityTypeEnum.RUNNING, title="Morning High-Pace Interval Run", duration_minutes=40, calories_burned=410.0, intensity=WorkoutIntensityEnum.HIGH, logged_date=date.today())
            daily_act = DailyActivitySummary(user_id=patient.id, date=date.today(), steps=8750, active_minutes=45, sleep_hours=7.8, sleep_quality=5, water_ml=2400, stress_level=3)
            db.add_all([workout, daily_act])

            # Mood Check-In
            mood = MoodLog(user_id=patient.id, mood_score=5, primary_emotion=EmotionEnum.ENERGETIC, journal_text="Solid morning workout and clarity for today's health goals.", gratitude_note="Grateful for energy and good cardiovascular stamina.", logged_date=date.today())
            db.add(mood)

            # Doctor Access Grant (24 hours)
            grant = PatientAccessGrant(
                patient_id=patient.id,
                access_token="DEMO-DOCTOR-ACCESS-PASS-2026",
                access_scope=AccessScopeEnum.FULL_ACCESS,
                expires_at=now + timedelta(hours=24),
                status=GrantStatusEnum.ACTIVE,
                notes="Demo Clinical Pass for Project Defense",
            )
            db.add(grant)

            # Timeline Events
            t1 = HealthTimelineEvent(user_id=patient.id, category=TimelineCategoryEnum.CLINICAL, event_type=TimelineEventTypeEnum.REPORT_CONFIRMED, title="Lipid Profile Confirmed", summary="Total Cholesterol 195 mg/dL, HDL 58 mg/dL, LDL 112 mg/dL", occurred_at=now - timedelta(days=5))
            t2 = HealthTimelineEvent(user_id=patient.id, category=TimelineCategoryEnum.MEDICATION, event_type=TimelineEventTypeEnum.MEDICATION_STARTED, title="Prescription Started: Metformin & Omega-3", summary="Initiated daily routine for cardiovascular and metabolic balance", occurred_at=now - timedelta(days=14))
            db.add_all([t1, t2])

            await db.commit()
            print("[WellNexa AI] Demo patient account created: patient@wellnexa.ai / Password123!")

        # 3. Doctor User: doctor@wellnexa.ai
        doc_q = select(User).where(User.email == "doctor@wellnexa.ai")
        doc_res = await db.execute(doc_q)
        doctor = doc_res.scalar_one_or_none()

        if not doctor:
            doctor = User(
                email="doctor@wellnexa.ai",
                hashed_password=get_password_hash("Password123!"),
                is_active=True,
                is_verified=True,
            )
            doctor.roles.append(roles_dict[RoleEnum.DOCTOR])
            db.add(doctor)
            await db.flush()

            doc_profile = Profile(
                user_id=doctor.id,
                first_name="Dr. Helen",
                last_name="Cho",
                gender=GenderEnum.FEMALE,
                blood_group=BloodGroupEnum.A_POSITIVE,
            )
            db.add(doc_profile)
            await db.commit()
            print("[WellNexa AI] Demo doctor account created: doctor@wellnexa.ai / Password123!")

        print("[WellNexa AI] Demonstration data seeding successfully completed.")

if __name__ == "__main__":
    asyncio.run(seed_all())
