import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func, delete

from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.health import (
    HealthMetric,
    MetricTypeEnum,
    MetricSourceEnum,
    Allergy,
    MedicalCondition,
    HealthGoal,
    LifestyleProfile,
)
from app.models.timeline import TimelineCategoryEnum, TimelineEventTypeEnum
from app.modules.timeline.service import TimelineService
from app.modules.health.schemas import (
    MetricCreateItem,
    MetricTrendResponse,
    MetricTrendPoint,
    AllergyCreateRequest,
    ConditionCreateRequest,
    GoalCreateRequest,
    LifestyleUpdateRequest,
    UnifiedHealthSummaryResponse,
    MetricResponse,
    AllergyResponse,
    ConditionResponse,
    GoalResponse,
    LifestyleResponse,
)

class HealthMetricService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.timeline_service = TimelineService(db)

    async def log_metrics(self, user_id: uuid.UUID, items: List[MetricCreateItem]) -> List[HealthMetric]:
        """Log one or multiple health metrics and auto-compute BMI if weight/height are provided."""
        created_metrics: List[HealthMetric] = []
        weight_val: Optional[float] = None
        height_val: Optional[float] = None

        for item in items:
            recorded_at = item.recorded_at or datetime.now(timezone.utc)
            metric = HealthMetric(
                user_id=user_id,
                metric_type=item.metric_type,
                value=item.value,
                unit=item.unit,
                recorded_at=recorded_at,
                source=item.source,
                notes=item.notes,
                metadata_info=item.metadata_info or {},
            )
            self.db.add(metric)
            created_metrics.append(metric)

            # Record timeline event for vitals
            m_name = item.metric_type.value.replace("_", " ").title()
            await self.timeline_service.record_event(
                user_id=user_id,
                category=TimelineCategoryEnum.CLINICAL,
                event_type=TimelineEventTypeEnum.METRIC_LOGGED,
                title=f"{m_name} Logged",
                summary=f"Recorded {m_name}: {item.value} {item.unit}",
                occurred_at=recorded_at,
                reference_id=str(metric.id),
                reference_type="health_metric",
                metadata_info={"metric_type": item.metric_type.value, "value": item.value, "unit": item.unit},
            )

            if item.metric_type == MetricTypeEnum.WEIGHT:
                weight_val = item.value
            elif item.metric_type == MetricTypeEnum.HEIGHT:
                height_val = item.value

        await self.db.flush()

        # Handle automated BMI calculation
        if weight_val is not None or height_val is not None:
            await self._calculate_and_record_bmi(user_id, weight_val, height_val)

        return created_metrics

    async def _calculate_and_record_bmi(
        self, user_id: uuid.UUID, weight_val: Optional[float], height_val: Optional[float]
    ) -> Optional[HealthMetric]:
        """Retrieve most recent weight and height to compute and persist BMI."""
        if weight_val is None:
            w_q = select(HealthMetric).where(
                and_(HealthMetric.user_id == user_id, HealthMetric.metric_type == MetricTypeEnum.WEIGHT)
            ).order_by(desc(HealthMetric.recorded_at)).limit(1)
            w_res = await self.db.execute(w_q)
            w_metric = w_res.scalar_one_or_none()
            if w_metric:
                weight_val = w_metric.value

        if height_val is None:
            h_q = select(HealthMetric).where(
                and_(HealthMetric.user_id == user_id, HealthMetric.metric_type == MetricTypeEnum.HEIGHT)
            ).order_by(desc(HealthMetric.recorded_at)).limit(1)
            h_res = await self.db.execute(h_q)
            h_metric = h_res.scalar_one_or_none()
            if h_metric:
                height_val = h_metric.value

        if weight_val and height_val and height_val > 0:
            height_in_m = height_val / 100.0 if height_val > 3.0 else height_val
            bmi_val = round(weight_val / (height_in_m ** 2), 2)
            now = datetime.now(timezone.utc)

            bmi_metric = HealthMetric(
                user_id=user_id,
                metric_type=MetricTypeEnum.BMI,
                value=bmi_val,
                unit="kg/m²",
                recorded_at=now,
                source=MetricSourceEnum.SYSTEM_CALCULATED,
                notes=f"Auto-calculated from weight ({weight_val} kg) and height ({height_val} {'cm' if height_val > 3 else 'm'})",
            )
            self.db.add(bmi_metric)
            await self.db.flush()

            # Record timeline event for BMI update
            await self.timeline_service.record_event(
                user_id=user_id,
                category=TimelineCategoryEnum.CLINICAL,
                event_type=TimelineEventTypeEnum.METRIC_LOGGED,
                title="BMI Updated",
                summary=f"BMI automatically computed: {bmi_val} kg/m²",
                occurred_at=now,
                reference_id=str(bmi_metric.id),
                reference_type="health_metric",
                metadata_info={"bmi": bmi_val, "weight": weight_val, "height": height_val},
            )

            return bmi_metric

        return None

    async def get_metrics(
        self,
        user_id: uuid.UUID,
        metric_type: Optional[MetricTypeEnum] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[HealthMetric]:
        query = select(HealthMetric).where(HealthMetric.user_id == user_id)
        if metric_type:
            query = query.where(HealthMetric.metric_type == metric_type)
        if start_date:
            query = query.where(HealthMetric.recorded_at >= start_date)
        if end_date:
            query = query.where(HealthMetric.recorded_at <= end_date)

        query = query.order_by(desc(HealthMetric.recorded_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_metric_trends(
        self, user_id: uuid.UUID, metric_type: MetricTypeEnum, days: int = 30
    ) -> MetricTrendResponse:
        since_time = datetime.now(timezone.utc) - timedelta(days=days)
        query = select(HealthMetric).where(
            and_(
                HealthMetric.user_id == user_id,
                HealthMetric.metric_type == metric_type,
                HealthMetric.recorded_at >= since_time,
            )
        ).order_by(HealthMetric.recorded_at.asc())

        result = await self.db.execute(query)
        metrics = list(result.scalars().all())

        if not metrics:
            return MetricTrendResponse(
                metric_type=metric_type.value if hasattr(metric_type, "value") else str(metric_type),
                unit="",
                latest_value=None,
                min_value=None,
                max_value=None,
                avg_value=None,
                data_points=[],
            )

        values = [m.value for m in metrics]
        data_points = [
            MetricTrendPoint(timestamp=m.recorded_at, value=m.value, unit=m.unit)
            for m in metrics
        ]

        return MetricTrendResponse(
            metric_type=metric_type.value if hasattr(metric_type, "value") else str(metric_type),
            unit=metrics[-1].unit,
            latest_value=values[-1],
            min_value=min(values),
            max_value=max(values),
            avg_value=round(sum(values) / len(values), 2),
            data_points=data_points,
        )

    async def delete_metric(self, user_id: uuid.UUID, metric_id: uuid.UUID) -> None:
        query = select(HealthMetric).where(
            and_(HealthMetric.id == metric_id, HealthMetric.user_id == user_id)
        )
        result = await self.db.execute(query)
        metric = result.scalar_one_or_none()
        if not metric:
            raise NotFoundException("HealthMetric", metric_id)
        await self.db.delete(metric)
        await self.db.flush()


class HealthProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.timeline_service = TimelineService(db)

    # Allergies
    async def create_allergy(self, user_id: uuid.UUID, req: AllergyCreateRequest) -> Allergy:
        allergy = Allergy(
            user_id=user_id,
            allergen=req.allergen.strip(),
            reaction=req.reaction.strip() if req.reaction else None,
            severity=req.severity,
            is_active=req.is_active,
        )
        self.db.add(allergy)
        await self.db.flush()

        # Timeline event
        await self.timeline_service.record_event(
            user_id=user_id,
            category=TimelineCategoryEnum.CLINICAL,
            event_type=TimelineEventTypeEnum.SYSTEM_NOTICE,
            title="Allergy Added",
            summary=f"Allergy to {req.allergen} ({req.severity.value}) recorded.",
            reference_id=str(allergy.id),
            reference_type="allergy",
        )

        return allergy

    async def get_allergies(self, user_id: uuid.UUID) -> List[Allergy]:
        query = select(Allergy).where(Allergy.user_id == user_id).order_by(desc(Allergy.created_at))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_allergy(self, user_id: uuid.UUID, allergy_id: uuid.UUID) -> None:
        query = select(Allergy).where(and_(Allergy.id == allergy_id, Allergy.user_id == user_id))
        result = await self.db.execute(query)
        allergy = result.scalar_one_or_none()
        if not allergy:
            raise NotFoundException("Allergy", allergy_id)
        await self.db.delete(allergy)
        await self.db.flush()

    # Medical Conditions
    async def create_condition(self, user_id: uuid.UUID, req: ConditionCreateRequest) -> MedicalCondition:
        condition = MedicalCondition(
            user_id=user_id,
            condition_name=req.condition_name.strip(),
            diagnosed_date=req.diagnosed_date,
            status=req.status,
            notes=req.notes,
        )
        self.db.add(condition)
        await self.db.flush()

        # Timeline event
        await self.timeline_service.record_event(
            user_id=user_id,
            category=TimelineCategoryEnum.CLINICAL,
            event_type=TimelineEventTypeEnum.SYSTEM_NOTICE,
            title="Medical Condition Logged",
            summary=f"Condition: {req.condition_name} ({req.status.value})",
            reference_id=str(condition.id),
            reference_type="medical_condition",
        )

        return condition

    async def get_conditions(self, user_id: uuid.UUID) -> List[MedicalCondition]:
        query = select(MedicalCondition).where(MedicalCondition.user_id == user_id).order_by(desc(MedicalCondition.created_at))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_condition(self, user_id: uuid.UUID, condition_id: uuid.UUID) -> None:
        query = select(MedicalCondition).where(and_(MedicalCondition.id == condition_id, MedicalCondition.user_id == user_id))
        result = await self.db.execute(query)
        cond = result.scalar_one_or_none()
        if not cond:
            raise NotFoundException("MedicalCondition", condition_id)
        await self.db.delete(cond)
        await self.db.flush()

    # Health Goals
    async def create_goal(self, user_id: uuid.UUID, req: GoalCreateRequest) -> HealthGoal:
        goal = HealthGoal(
            user_id=user_id,
            title=req.title.strip(),
            goal_type=req.goal_type.strip(),
            target_value=req.target_value,
            current_value=req.current_value,
            unit=req.unit.strip(),
            start_date=req.start_date or datetime.now(timezone.utc).date(),
            target_date=req.target_date,
            status=req.status,
            notes=req.notes,
        )
        self.db.add(goal)
        await self.db.flush()

        # Timeline event
        await self.timeline_service.record_event(
            user_id=user_id,
            category=TimelineCategoryEnum.FITNESS,
            event_type=TimelineEventTypeEnum.GOAL_ACHIEVED if req.status == "ACHIEVED" else TimelineEventTypeEnum.SYSTEM_NOTICE,
            title=f"Health Goal: {req.title}",
            summary=f"Target: {req.target_value} {req.unit}",
            reference_id=str(goal.id),
            reference_type="health_goal",
        )

        return goal

    async def get_goals(self, user_id: uuid.UUID) -> List[HealthGoal]:
        query = select(HealthGoal).where(HealthGoal.user_id == user_id).order_by(desc(HealthGoal.created_at))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_goal(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> None:
        query = select(HealthGoal).where(and_(HealthGoal.id == goal_id, HealthGoal.user_id == user_id))
        result = await self.db.execute(query)
        goal = result.scalar_one_or_none()
        if not goal:
            raise NotFoundException("HealthGoal", goal_id)
        await self.db.delete(goal)
        await self.db.flush()

    # Lifestyle Profile
    async def get_or_create_lifestyle(self, user_id: uuid.UUID) -> LifestyleProfile:
        query = select(LifestyleProfile).where(LifestyleProfile.user_id == user_id)
        result = await self.db.execute(query)
        profile = result.scalar_one_or_none()
        if not profile:
            profile = LifestyleProfile(user_id=user_id)
            self.db.add(profile)
            await self.db.flush()
        return profile

    async def update_lifestyle(self, user_id: uuid.UUID, req: LifestyleUpdateRequest) -> LifestyleProfile:
        profile = await self.get_or_create_lifestyle(user_id)
        if req.diet_type is not None:
            profile.diet_type = req.diet_type
        if req.activity_level is not None:
            profile.activity_level = req.activity_level
        if req.smoking_status is not None:
            profile.smoking_status = req.smoking_status
        if req.alcohol_status is not None:
            profile.alcohol_status = req.alcohol_status
        if req.sleep_target_hours is not None:
            profile.sleep_target_hours = req.sleep_target_hours
        if req.water_target_liters is not None:
            profile.water_target_liters = req.water_target_liters

        await self.db.flush()
        return profile

    # Unified Health Summary
    async def get_unified_summary(self, user_id: uuid.UUID) -> UnifiedHealthSummaryResponse:
        async def get_latest_metric(m_type: MetricTypeEnum) -> Optional[MetricResponse]:
            q = select(HealthMetric).where(
                and_(HealthMetric.user_id == user_id, HealthMetric.metric_type == m_type)
            ).order_by(desc(HealthMetric.recorded_at)).limit(1)
            res = await self.db.execute(q)
            m = res.scalar_one_or_none()
            if not m:
                return None
            return MetricResponse(
                id=m.id,
                user_id=m.user_id,
                metric_type=m.metric_type.value if hasattr(m.metric_type, "value") else str(m.metric_type),
                value=m.value,
                unit=m.unit,
                recorded_at=m.recorded_at,
                source=m.source.value if hasattr(m.source, "value") else str(m.source),
                notes=m.notes,
            )

        bmi = await get_latest_metric(MetricTypeEnum.BMI)
        weight = await get_latest_metric(MetricTypeEnum.WEIGHT)
        height = await get_latest_metric(MetricTypeEnum.HEIGHT)
        bp_sys = await get_latest_metric(MetricTypeEnum.BLOOD_PRESSURE_SYSTOLIC)
        bp_dia = await get_latest_metric(MetricTypeEnum.BLOOD_PRESSURE_DIASTOLIC)
        glucose = await get_latest_metric(MetricTypeEnum.BLOOD_GLUCOSE_FASTING)

        allergies = await self.get_allergies(user_id)
        conditions = await self.get_conditions(user_id)
        goals = await self.get_goals(user_id)
        lifestyle = await self.get_or_create_lifestyle(user_id)

        return UnifiedHealthSummaryResponse(
            bmi=bmi,
            latest_weight=weight,
            latest_height=height,
            latest_bp_systolic=bp_sys,
            latest_bp_diastolic=bp_dia,
            latest_blood_glucose=glucose,
            active_allergies=[
                AllergyResponse(
                    id=a.id,
                    allergen=a.allergen,
                    reaction=a.reaction,
                    severity=a.severity.value if hasattr(a.severity, "value") else str(a.severity),
                    is_active=a.is_active,
                )
                for a in allergies if a.is_active
            ],
            active_conditions=[
                ConditionResponse(
                    id=c.id,
                    condition_name=c.condition_name,
                    diagnosed_date=c.diagnosed_date,
                    status=c.status.value if hasattr(c.status, "value") else str(c.status),
                    notes=c.notes,
                )
                for c in conditions
            ],
            active_goals=[
                GoalResponse(
                    id=g.id,
                    title=g.title,
                    goal_type=g.goal_type,
                    target_value=g.target_value,
                    current_value=g.current_value,
                    unit=g.unit,
                    start_date=g.start_date,
                    target_date=g.target_date,
                    status=g.status.value if hasattr(g.status, "value") else str(g.status),
                    notes=g.notes,
                )
                for g in goals
            ],
            lifestyle=LifestyleResponse(
                diet_type=lifestyle.diet_type,
                activity_level=lifestyle.activity_level,
                smoking_status=lifestyle.smoking_status,
                alcohol_status=lifestyle.alcohol_status,
                sleep_target_hours=lifestyle.sleep_target_hours,
                water_target_liters=lifestyle.water_target_liters,
            ),
        )
