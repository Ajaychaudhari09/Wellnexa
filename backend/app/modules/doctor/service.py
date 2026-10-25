import secrets
import uuid
from datetime import datetime, date, timedelta, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.core.exceptions import NotFoundException, PermissionDeniedException, WellNexaException
from app.models.user import User
from app.models.profile import Profile
from app.models.health import Allergy, MedicalCondition, HealthMetric
from app.models.medicine import Medication
from app.models.report import MedicalReport, ExtractionStatusEnum
from app.models.timeline import HealthTimelineEvent, TimelineCategoryEnum, TimelineEventTypeEnum
from app.models.audit import AuditLog
from app.models.doctor import (
    PatientAccessGrant,
    DoctorConsultation,
    AccessScopeEnum,
    GrantStatusEnum,
)
from app.modules.timeline.service import TimelineService
from app.modules.doctor.schemas import (
    CreateAccessGrantRequest,
    AccessGrantResponse,
    DoctorConsultationCreateRequest,
    DoctorConsultationResponse,
    PatientClinicalSummaryResponse,
    SharedMedicationItem,
    SharedReportItem,
)

class DoctorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.timeline_service = TimelineService(db)

    # ----------------- Access Grants (Patient controls) -----------------
    async def create_access_grant(self, patient_id: uuid.UUID, req: CreateAccessGrantRequest) -> AccessGrantResponse:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=req.duration_hours)
        token = secrets.token_urlsafe(32)

        # Check if doctor email provided
        doc_id = None
        if req.doctor_email:
            doc_q = select(User).where(User.email == req.doctor_email.strip().lower())
            doc_res = await self.db.execute(doc_q)
            doc_user = doc_res.scalar_one_or_none()
            if doc_user:
                doc_id = doc_user.id

        grant = PatientAccessGrant(
            patient_id=patient_id,
            doctor_id=doc_id,
            access_token=token,
            access_scope=req.access_scope,
            expires_at=expires,
            status=GrantStatusEnum.ACTIVE,
            notes=req.notes.strip() if req.notes else None,
        )
        self.db.add(grant)
        await self.db.flush()

        # Emit timeline event
        await self.timeline_service.record_event(
            user_id=patient_id,
            category=TimelineCategoryEnum.GENERAL,
            event_type=TimelineEventTypeEnum.SYSTEM_NOTICE,
            title="Doctor Access Grant Created",
            summary=f"Created {req.duration_hours}-hour secure clinical access grant ({req.access_scope.value.replace('_', ' ').title()}).",
            occurred_at=now,
            reference_id=str(grant.id),
            reference_type="access_grant",
        )

        return AccessGrantResponse(
            id=grant.id,
            patient_id=grant.patient_id,
            doctor_id=grant.doctor_id,
            access_token=grant.access_token,
            access_scope=grant.access_scope.value,
            expires_at=grant.expires_at,
            status=grant.status.value,
            notes=grant.notes,
            share_url=f"/portal/doctor/patient/{patient_id}?token={token}",
            created_at=grant.created_at,
        )

    async def get_patient_grants(self, patient_id: uuid.UUID) -> List[AccessGrantResponse]:
        now = datetime.now(timezone.utc)
        query = select(PatientAccessGrant).where(PatientAccessGrant.patient_id == patient_id).order_by(desc(PatientAccessGrant.created_at))
        result = await self.db.execute(query)
        grants = list(result.scalars().all())

        responses: List[AccessGrantResponse] = []
        for g in grants:
            g_exp = g.expires_at if g.expires_at.tzinfo else g.expires_at.replace(tzinfo=timezone.utc)
            if g.status == GrantStatusEnum.ACTIVE and g_exp < now:
                g.status = GrantStatusEnum.EXPIRED
            responses.append(
                AccessGrantResponse(
                    id=g.id,
                    patient_id=g.patient_id,
                    doctor_id=g.doctor_id,
                    access_token=g.access_token,
                    access_scope=g.access_scope.value,
                    expires_at=g.expires_at,
                    status=g.status.value,
                    notes=g.notes,
                    share_url=f"/portal/doctor/patient/{g.patient_id}?token={g.access_token}",
                    created_at=g.created_at,
                )
            )

        await self.db.flush()
        return responses

    async def revoke_access_grant(self, patient_id: uuid.UUID, grant_id: uuid.UUID) -> None:
        query = select(PatientAccessGrant).where(
            and_(PatientAccessGrant.id == grant_id, PatientAccessGrant.patient_id == patient_id)
        )
        result = await self.db.execute(query)
        grant = result.scalar_one_or_none()
        if not grant:
            raise NotFoundException("PatientAccessGrant", grant_id)

        grant.status = GrantStatusEnum.REVOKED
        await self.db.flush()

    # ----------------- Doctor Access Verification -----------------
    async def validate_grant(self, access_token: str, patient_id: uuid.UUID) -> PatientAccessGrant:
        now = datetime.now(timezone.utc)
        query = select(PatientAccessGrant).where(
            and_(
                PatientAccessGrant.access_token == access_token.strip(),
                PatientAccessGrant.patient_id == patient_id,
            )
        )
        result = await self.db.execute(query)
        grant = result.scalar_one_or_none()
        if not grant:
            raise PermissionDeniedException("Invalid or non-existent access token")

        grant_exp = grant.expires_at if grant.expires_at.tzinfo else grant.expires_at.replace(tzinfo=timezone.utc)
        if grant.status != GrantStatusEnum.ACTIVE or grant_exp < now:
            grant.status = GrantStatusEnum.EXPIRED
            await self.db.flush()
            raise PermissionDeniedException("Access grant has expired or been revoked")

        return grant

    # ----------------- Patient Clinical Summary (Doctor view) -----------------
    async def get_patient_clinical_summary(self, access_token: str, patient_id: uuid.UUID) -> PatientClinicalSummaryResponse:
        grant = await self.validate_grant(access_token, patient_id)
        scope = grant.access_scope

        # Profile
        prof_res = await self.db.execute(select(Profile).where(Profile.user_id == patient_id))
        prof = prof_res.scalar_one_or_none()
        full_name = f"{prof.first_name} {prof.last_name}" if prof else "WellNexa Patient"
        gender = prof.gender.value if prof and prof.gender else None
        blood = prof.blood_group.value if prof and prof.blood_group else None

        allergies: List[str] = []
        conditions: List[str] = []
        medications: List[SharedMedicationItem] = []
        metrics_dict: Dict[str, Any] = {}
        reports_list: List[SharedReportItem] = []
        timeline_events: List[Dict[str, Any]] = []

        # Allergies & Conditions (Included in FULL_ACCESS or VITALS_ONLY)
        if scope in (AccessScopeEnum.FULL_ACCESS, AccessScopeEnum.VITALS_ONLY):
            alg_res = await self.db.execute(select(Allergy).where(Allergy.user_id == patient_id))
            allergies = [f"{a.allergen} ({a.severity.value})" for a in alg_res.scalars().all()]

            cond_res = await self.db.execute(select(MedicalCondition).where(MedicalCondition.user_id == patient_id))
            conditions = [f"{c.condition_name} ({c.status.value})" for c in cond_res.scalars().all()]

        # Medications
        if scope in (AccessScopeEnum.FULL_ACCESS, AccessScopeEnum.MEDICATIONS_ONLY):
            med_res = await self.db.execute(select(Medication).where(and_(Medication.user_id == patient_id, Medication.is_active == True)))
            for m in med_res.scalars().all():
                medications.append(
                    SharedMedicationItem(
                        name=m.name,
                        dosage=m.dosage,
                        timing=m.timing.value,
                        frequency=m.frequency.value,
                        instructions=m.instructions,
                    )
                )

        # Vitals / Metrics
        if scope in (AccessScopeEnum.FULL_ACCESS, AccessScopeEnum.VITALS_ONLY):
            met_res = await self.db.execute(
                select(HealthMetric).where(HealthMetric.user_id == patient_id).order_by(desc(HealthMetric.recorded_at)).limit(10)
            )
            for met in met_res.scalars().all():
                m_type = met.metric_type.value
                if m_type not in metrics_dict:
                    metrics_dict[m_type] = {"latest_value": met.value, "unit": met.unit, "recorded_at": met.recorded_at}

        # Reports
        if scope in (AccessScopeEnum.FULL_ACCESS, AccessScopeEnum.REPORTS_ONLY):
            rep_res = await self.db.execute(
                select(MedicalReport).where(
                    and_(MedicalReport.user_id == patient_id, MedicalReport.status == ExtractionStatusEnum.CONFIRMED)
                ).order_by(desc(MedicalReport.created_at)).limit(5)
            )
            for r in rep_res.scalars().all():
                items_summary = [
                    {"test_name": e.test_name, "value": e.confirmed_value or e.detected_value, "unit": e.unit, "flag": e.flag_status.value}
                    for e in r.extractions
                ]
                reports_list.append(
                    SharedReportItem(
                        id=r.id,
                        report_type=r.report_type.value,
                        status=r.status.value,
                        created_at=r.created_at,
                        extractions_summary=items_summary,
                    )
                )

        # Timeline
        if scope == AccessScopeEnum.FULL_ACCESS:
            t_res = await self.db.execute(
                select(HealthTimelineEvent).where(HealthTimelineEvent.user_id == patient_id).order_by(desc(HealthTimelineEvent.occurred_at)).limit(10)
            )
            for ev in t_res.scalars().all():
                timeline_events.append({
                    "title": ev.title,
                    "summary": ev.summary,
                    "category": ev.category.value,
                    "occurred_at": ev.occurred_at,
                })

        return PatientClinicalSummaryResponse(
            patient_id=patient_id,
            full_name=full_name,
            gender=gender,
            blood_group=blood,
            allergies=allergies,
            chronic_conditions=conditions,
            active_medications=medications,
            recent_metrics=metrics_dict,
            confirmed_reports=reports_list,
            recent_timeline_events=timeline_events,
            access_scope=scope.value,
            grant_expires_at=grant.expires_at,
        )

    # ----------------- Doctor Consultation Notes -----------------
    async def create_consultation_note(
        self, patient_id: uuid.UUID, req: DoctorConsultationCreateRequest, doctor_id: Optional[uuid.UUID] = None
    ) -> DoctorConsultation:
        consultation = DoctorConsultation(
            patient_id=patient_id,
            doctor_id=doctor_id,
            doctor_name=req.doctor_name.strip(),
            clinic_name=req.clinic_name.strip() if req.clinic_name else None,
            consultation_date=req.consultation_date or datetime.now(timezone.utc).date(),
            chief_complaint=req.chief_complaint.strip(),
            clinical_observations=req.clinical_observations.strip() if req.clinical_observations else None,
            recommended_actions=req.recommended_actions.strip() if req.recommended_actions else None,
            follow_up_date=req.follow_up_date,
        )
        self.db.add(consultation)
        await self.db.flush()

        # Emit timeline event
        await self.timeline_service.record_event(
            user_id=patient_id,
            category=TimelineCategoryEnum.CLINICAL,
            event_type=TimelineEventTypeEnum.APPOINTMENT_SCHEDULED,
            title=f"Doctor Consultation: {consultation.doctor_name}",
            summary=f"Chief Complaint: '{consultation.chief_complaint}' • Actions: '{consultation.recommended_actions or 'Follow regimen'}'",
            occurred_at=datetime.now(timezone.utc),
            reference_id=str(consultation.id),
            reference_type="doctor_consultation",
        )

        return consultation

    async def get_patient_consultations(self, patient_id: uuid.UUID) -> List[DoctorConsultation]:
        query = select(DoctorConsultation).where(DoctorConsultation.patient_id == patient_id).order_by(desc(DoctorConsultation.consultation_date))
        result = await self.db.execute(query)
        return list(result.scalars().all())
