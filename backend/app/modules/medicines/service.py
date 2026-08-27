import uuid
from datetime import datetime, date, timedelta, timezone
from typing import List, Optional, Tuple, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.core.exceptions import NotFoundException, WellNexaException
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
from app.models.timeline import TimelineCategoryEnum, TimelineEventTypeEnum
from app.models.audit import AuditLog
from app.modules.timeline.service import TimelineService
from app.modules.medicines.schemas import (
    PrescriptionCreateRequest,
    MedicationCreateRequest,
    MedicationUpdateRequest,
    LogDoseRequest,
    TodayDoseItem,
    TodayMedicationScheduleResponse,
    MonthlyAdherenceItem,
    AdherenceScoreResponse,
    RefillAlertItem,
    RefillAlertResponse,
)

class MedicineService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.timeline_service = TimelineService(db)

    # ----------------- Prescriptions -----------------
    async def create_prescription(self, user_id: uuid.UUID, req: PrescriptionCreateRequest) -> Prescription:
        presc = Prescription(
            user_id=user_id,
            document_id=req.document_id,
            doctor_name=req.doctor_name.strip() if req.doctor_name else None,
            clinic_name=req.clinic_name.strip() if req.clinic_name else None,
            prescribed_date=req.prescribed_date or datetime.now(timezone.utc).date(),
            diagnosis_notes=req.diagnosis_notes.strip() if req.diagnosis_notes else None,
        )
        self.db.add(presc)
        await self.db.flush()

        # Emit timeline event
        await self.timeline_service.record_event(
            user_id=user_id,
            category=TimelineCategoryEnum.MEDICATION,
            event_type=TimelineEventTypeEnum.PRESCRIPTION_ADDED,
            title="Prescription Added",
            summary=f"Prescription from {req.doctor_name or 'Doctor'} on {presc.prescribed_date}",
            occurred_at=datetime.now(timezone.utc),
            reference_id=str(presc.id),
            reference_type="prescription",
        )

        return presc

    async def get_prescriptions(self, user_id: uuid.UUID) -> List[Prescription]:
        query = select(Prescription).where(Prescription.user_id == user_id).order_by(desc(Prescription.prescribed_date))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ----------------- Medications -----------------
    async def add_medication(self, user_id: uuid.UUID, req: MedicationCreateRequest) -> Medication:
        med = Medication(
            user_id=user_id,
            prescription_id=req.prescription_id,
            name=req.name.strip(),
            dosage=req.dosage.strip(),
            form=req.form,
            frequency=req.frequency,
            timing=req.timing,
            instructions=req.instructions.strip() if req.instructions else None,
            start_date=req.start_date or datetime.now(timezone.utc).date(),
            end_date=req.end_date,
            current_stock=req.current_stock,
            refill_threshold=req.refill_threshold,
            is_active=True,
        )
        self.db.add(med)
        await self.db.flush()

        # Default schedule times if none provided based on frequency
        schedules_to_add = req.schedules
        if not schedules_to_add:
            if req.frequency == FrequencyEnum.ONCE_DAILY:
                schedules_to_add = [type("item", (), {"time_slot": "09:00", "dosage_quantity": 1.0, "days_of_week": "DAILY"})]
            elif req.frequency == FrequencyEnum.TWICE_DAILY:
                schedules_to_add = [
                    type("item", (), {"time_slot": "09:00", "dosage_quantity": 1.0, "days_of_week": "DAILY"}),
                    type("item", (), {"time_slot": "21:00", "dosage_quantity": 1.0, "days_of_week": "DAILY"}),
                ]
            elif req.frequency == FrequencyEnum.THRICE_DAILY:
                schedules_to_add = [
                    type("item", (), {"time_slot": "08:00", "dosage_quantity": 1.0, "days_of_week": "DAILY"}),
                    type("item", (), {"time_slot": "14:00", "dosage_quantity": 1.0, "days_of_week": "DAILY"}),
                    type("item", (), {"time_slot": "20:00", "dosage_quantity": 1.0, "days_of_week": "DAILY"}),
                ]

        for s in schedules_to_add:
            sched = MedicationSchedule(
                medication_id=med.id,
                time_slot=s.time_slot,
                dosage_quantity=s.dosage_quantity,
                days_of_week=s.days_of_week or "DAILY",
            )
            self.db.add(sched)

        await self.db.flush()

        # Health Timeline Event
        await self.timeline_service.record_event(
            user_id=user_id,
            category=TimelineCategoryEnum.MEDICATION,
            event_type=TimelineEventTypeEnum.MEDICATION_STARTED,
            title=f"Started Medication: {med.name}",
            summary=f"{med.dosage} • {med.frequency.value.replace('_', ' ').title()} • {med.timing.value.replace('_', ' ').title()}",
            occurred_at=datetime.now(timezone.utc),
            reference_id=str(med.id),
            reference_type="medication",
            metadata_info={"name": med.name, "dosage": med.dosage, "form": med.form.value},
        )

        # Audit Log
        audit = AuditLog(
            user_id=user_id,
            action="MEDICATION_ADDED",
            resource="medications",
            resource_id=str(med.id),
            details={"name": med.name, "dosage": med.dosage},
        )
        self.db.add(audit)
        await self.db.flush()

        # Re-fetch with schedules
        q = select(Medication).where(Medication.id == med.id)
        res = await self.db.execute(q)
        return res.scalar_one()

    async def get_medications(self, user_id: uuid.UUID, is_active: Optional[bool] = None) -> List[Medication]:
        query = select(Medication).where(Medication.user_id == user_id)
        if is_active is not None:
            query = query.where(Medication.is_active == is_active)
        query = query.order_by(desc(Medication.created_at))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_medication_by_id(self, user_id: uuid.UUID, medication_id: uuid.UUID) -> Medication:
        query = select(Medication).where(
            and_(Medication.id == medication_id, Medication.user_id == user_id)
        )
        result = await self.db.execute(query)
        med = result.scalar_one_or_none()
        if not med:
            raise NotFoundException("Medication", medication_id)
        return med

    async def update_medication(self, user_id: uuid.UUID, medication_id: uuid.UUID, req: MedicationUpdateRequest) -> Medication:
        med = await self.get_medication_by_id(user_id, medication_id)
        if req.name is not None:
            med.name = req.name.strip()
        if req.dosage is not None:
            med.dosage = req.dosage.strip()
        if req.form is not None:
            med.form = req.form
        if req.frequency is not None:
            med.frequency = req.frequency
        if req.timing is not None:
            med.timing = req.timing
        if req.instructions is not None:
            med.instructions = req.instructions.strip()
        if req.end_date is not None:
            med.end_date = req.end_date
        if req.current_stock is not None:
            med.current_stock = req.current_stock
        if req.refill_threshold is not None:
            med.refill_threshold = req.refill_threshold
        if req.is_active is not None:
            med.is_active = req.is_active
        await self.db.flush()
        return med

    # ----------------- Dose Logging -----------------
    async def log_dose(
        self, user_id: uuid.UUID, medication_id: uuid.UUID, req: LogDoseRequest
    ) -> MedicationLog:
        """Record a dose status (TAKEN/MISSED/SKIPPED) and update inventory stock."""
        med = await self.get_medication_by_id(user_id, medication_id)
        now = datetime.now(timezone.utc)
        scheduled_at = req.scheduled_at or now

        # Create dose log
        log = MedicationLog(
            medication_id=med.id,
            user_id=user_id,
            scheduled_at=scheduled_at,
            status=req.status,
            taken_at=req.taken_at or (now if req.status == DoseStatusEnum.TAKEN else None),
            notes=req.notes.strip() if req.notes else None,
        )
        self.db.add(log)

        # If dose was taken, decrement inventory count
        if req.status == DoseStatusEnum.TAKEN:
            if med.current_stock > 0:
                med.current_stock -= 1

            # Dispatch timeline event
            await self.timeline_service.record_event(
                user_id=user_id,
                category=TimelineCategoryEnum.MEDICATION,
                event_type=TimelineEventTypeEnum.REMINDER_COMPLETED,
                title=f"Dose Taken: {med.name}",
                summary=f"Took {med.name} ({med.dosage}) at {now.strftime('%I:%M %p')}",
                occurred_at=now,
                reference_id=str(log.id),
                reference_type="medication_log",
            )

        await self.db.flush()
        return log

    # ----------------- Today's Schedule -----------------
    async def get_today_schedule(self, user_id: uuid.UUID, target_date: Optional[date] = None) -> TodayMedicationScheduleResponse:
        t_date = target_date or datetime.now(timezone.utc).date()
        active_meds = await self.get_medications(user_id, is_active=True)

        dose_items: List[TodayDoseItem] = []
        total_doses = 0
        taken_doses = 0

        for med in active_meds:
            for sched in med.schedules:
                total_doses += 1
                
                # Check if a log exists for today & this medication
                log_q = select(MedicationLog).where(
                    and_(
                        MedicationLog.user_id == user_id,
                        MedicationLog.medication_id == med.id,
                        func.date(MedicationLog.scheduled_at) == t_date,
                    )
                ).order_by(desc(MedicationLog.created_at)).limit(1)
                log_res = await self.db.execute(log_q)
                dose_log = log_res.scalar_one_or_none()

                status_val = dose_log.status.value if dose_log else "SCHEDULED"
                if status_val == "TAKEN":
                    taken_doses += 1

                dose_items.append(
                    TodayDoseItem(
                        medication_id=med.id,
                        medication_name=med.name,
                        dosage=med.dosage,
                        timing=med.timing.value.replace("_", " ").title(),
                        time_slot=sched.time_slot,
                        status=status_val,
                        log_id=dose_log.id if dose_log else None,
                    )
                )

        return TodayMedicationScheduleResponse(
            date=t_date,
            total_doses=total_doses,
            taken_doses=taken_doses,
            pending_doses=max(0, total_doses - taken_doses),
            doses=dose_items,
        )

    # ----------------- Adherence Score Engine -----------------
    async def calculate_adherence_score(self, user_id: uuid.UUID, days: int = 30) -> AdherenceScoreResponse:
        """Calculate overall and monthly adherence scores: Adherence = (taken / total) * 100%."""
        since_time = datetime.now(timezone.utc) - timedelta(days=days)
        query = select(MedicationLog).where(
            and_(
                MedicationLog.user_id == user_id,
                MedicationLog.scheduled_at >= since_time,
            )
        ).order_by(MedicationLog.scheduled_at.asc())

        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        total_scheduled = len(logs)
        total_taken = sum(1 for l in logs if l.status == DoseStatusEnum.TAKEN)
        total_missed = sum(1 for l in logs if l.status == DoseStatusEnum.MISSED)

        if total_scheduled == 0:
            overall_pct = 100.0
            tier = "EXCELLENT"
        else:
            overall_pct = round((total_taken / total_scheduled) * 100, 1)
            if overall_pct >= 90.0:
                tier = "EXCELLENT"
            elif overall_pct >= 80.0:
                tier = "GOOD"
            else:
                tier = "NEEDS_ATTENTION"

        # Group by month
        monthly_groups: Dict[str, Dict[str, int]] = {}
        for l in logs:
            m_label = l.scheduled_at.strftime("%b %Y")
            if m_label not in monthly_groups:
                monthly_groups[m_label] = {"scheduled": 0, "taken": 0, "missed": 0}
            monthly_groups[m_label]["scheduled"] += 1
            if l.status == DoseStatusEnum.TAKEN:
                monthly_groups[m_label]["taken"] += 1
            elif l.status == DoseStatusEnum.MISSED:
                monthly_groups[m_label]["missed"] += 1

        monthly_history: List[MonthlyAdherenceItem] = []
        for m_label, stats in monthly_groups.items():
            s_cnt = stats["scheduled"]
            t_cnt = stats["taken"]
            pct = round((t_cnt / s_cnt) * 100, 1) if s_cnt > 0 else 100.0
            monthly_history.append(
                MonthlyAdherenceItem(
                    month_label=m_label,
                    scheduled_count=s_cnt,
                    taken_count=t_cnt,
                    missed_count=stats["missed"],
                    adherence_percentage=pct,
                )
            )

        return AdherenceScoreResponse(
            total_scheduled=total_scheduled,
            total_taken=total_taken,
            total_missed=total_missed,
            overall_adherence_percentage=overall_pct,
            adherence_tier=tier,
            monthly_history=monthly_history,
        )

    # ----------------- Refill Alerts -----------------
    async def get_refill_alerts(self, user_id: uuid.UUID) -> RefillAlertResponse:
        """Find active medications whose stock has dropped to or below the refill threshold."""
        meds = await self.get_medications(user_id, is_active=True)
        alerts: List[RefillAlertItem] = []

        for m in meds:
            if m.current_stock <= m.refill_threshold:
                urgency = "URGENT" if m.current_stock <= 2 else "WARNING"
                alerts.append(
                    RefillAlertItem(
                        medication_id=m.id,
                        medication_name=m.name,
                        dosage=m.dosage,
                        current_stock=m.current_stock,
                        refill_threshold=m.refill_threshold,
                        days_supply_remaining=m.current_stock, # Approximation assuming 1/day
                        refill_urgency=urgency,
                    )
                )

        return RefillAlertResponse(
            total_alerts=len(alerts),
            medications_requiring_refill=alerts,
        )
