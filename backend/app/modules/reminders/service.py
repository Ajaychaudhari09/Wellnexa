import uuid
from datetime import datetime, date, timezone
from typing import List, Optional, Tuple, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.core.exceptions import NotFoundException, WellNexaException
from app.models.reminder import (
    Reminder,
    ReminderLog,
    NotificationPreference,
    ReminderTypeEnum,
    RecurrenceTypeEnum,
    ReminderStatusEnum,
)
from app.models.timeline import TimelineCategoryEnum, TimelineEventTypeEnum
from app.models.audit import AuditLog
from app.modules.timeline.service import TimelineService
from app.modules.reminders.schemas import (
    ReminderCreateRequest,
    ReminderUpdateRequest,
    ReminderActionRequest,
    DueReminderItem,
    TodayUpcomingRemindersResponse,
    NotificationPreferenceUpdateRequest,
)

class ReminderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.timeline_service = TimelineService(db)

    async def create_reminder(self, user_id: uuid.UUID, req: ReminderCreateRequest) -> Reminder:
        reminder = Reminder(
            user_id=user_id,
            reminder_type=req.reminder_type,
            title=req.title.strip(),
            description=req.description.strip() if req.description else None,
            recurrence=req.recurrence,
            due_date=req.due_date,
            due_time=req.due_time.strip(),
            days_of_week=req.days_of_week or "DAILY",
            is_active=True,
            reference_id=req.reference_id,
            reference_type=req.reference_type,
            metadata_info=req.metadata_info or {},
        )
        self.db.add(reminder)
        await self.db.flush()

        # Emit timeline event for clinical/habit reminders
        category_map = {
            ReminderTypeEnum.MEDICINE: TimelineCategoryEnum.MEDICATION,
            ReminderTypeEnum.APPOINTMENT: TimelineCategoryEnum.APPOINTMENT,
            ReminderTypeEnum.LAB_TEST: TimelineCategoryEnum.CLINICAL,
            ReminderTypeEnum.CHECKUP: TimelineCategoryEnum.CLINICAL,
            ReminderTypeEnum.REFILL: TimelineCategoryEnum.MEDICATION,
            ReminderTypeEnum.WATER: TimelineCategoryEnum.WELLNESS,
            ReminderTypeEnum.EXERCISE: TimelineCategoryEnum.FITNESS,
            ReminderTypeEnum.WELLNESS: TimelineCategoryEnum.WELLNESS,
            ReminderTypeEnum.CUSTOM: TimelineCategoryEnum.GENERAL,
        }

        await self.timeline_service.record_event(
            user_id=user_id,
            category=category_map.get(req.reminder_type, TimelineCategoryEnum.REMINDER),
            event_type=TimelineEventTypeEnum.SYSTEM_NOTICE,
            title=f"Reminder Set: {reminder.title}",
            summary=f"{req.reminder_type.value.replace('_', ' ').title()} • {req.recurrence.value.title()} at {reminder.due_time}",
            occurred_at=datetime.now(timezone.utc),
            reference_id=str(reminder.id),
            reference_type="reminder",
        )

        return reminder

    async def get_user_reminders(
        self, user_id: uuid.UUID, reminder_type: Optional[ReminderTypeEnum] = None, is_active: Optional[bool] = None
    ) -> List[Reminder]:
        query = select(Reminder).where(Reminder.user_id == user_id)
        if reminder_type:
            query = query.where(Reminder.reminder_type == reminder_type)
        if is_active is not None:
            query = query.where(Reminder.is_active == is_active)
        query = query.order_by(Reminder.due_time.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_reminder_by_id(self, user_id: uuid.UUID, reminder_id: uuid.UUID) -> Reminder:
        query = select(Reminder).where(
            and_(Reminder.id == reminder_id, Reminder.user_id == user_id)
        )
        result = await self.db.execute(query)
        rem = result.scalar_one_or_none()
        if not rem:
            raise NotFoundException("Reminder", reminder_id)
        return rem

    async def update_reminder(
        self, user_id: uuid.UUID, reminder_id: uuid.UUID, req: ReminderUpdateRequest
    ) -> Reminder:
        rem = await self.get_reminder_by_id(user_id, reminder_id)
        if req.title is not None:
            rem.title = req.title.strip()
        if req.description is not None:
            rem.description = req.description.strip()
        if req.recurrence is not None:
            rem.recurrence = req.recurrence
        if req.due_date is not None:
            rem.due_date = req.due_date
        if req.due_time is not None:
            rem.due_time = req.due_time.strip()
        if req.days_of_week is not None:
            rem.days_of_week = req.days_of_week
        if req.is_active is not None:
            rem.is_active = req.is_active
        await self.db.flush()
        return rem

    async def delete_reminder(self, user_id: uuid.UUID, reminder_id: uuid.UUID) -> None:
        rem = await self.get_reminder_by_id(user_id, reminder_id)
        await self.db.delete(rem)
        await self.db.flush()

    async def get_today_due_reminders(
        self, user_id: uuid.UUID, target_date: Optional[date] = None
    ) -> TodayUpcomingRemindersResponse:
        t_date = target_date or datetime.now(timezone.utc).date()
        reminders = await self.get_user_reminders(user_id, is_active=True)

        due_items: List[DueReminderItem] = []
        completed_count = 0

        for r in reminders:
            # Check if one-time reminder has passed
            if r.recurrence == RecurrenceTypeEnum.ONCE and r.due_date and r.due_date != t_date:
                continue

            # Query log for today
            log_q = select(ReminderLog).where(
                and_(
                    ReminderLog.user_id == user_id,
                    ReminderLog.reminder_id == r.id,
                    func.date(ReminderLog.scheduled_at) == t_date,
                )
            ).order_by(desc(ReminderLog.created_at)).limit(1)
            log_res = await self.db.execute(log_q)
            rem_log = log_res.scalar_one_or_none()

            status_str = rem_log.status.value if rem_log else "PENDING"
            if status_str == "COMPLETED":
                completed_count += 1

            due_items.append(
                DueReminderItem(
                    reminder_id=r.id,
                    reminder_type=r.reminder_type.value,
                    title=r.title,
                    description=r.description,
                    due_time=r.due_time,
                    recurrence=r.recurrence.value,
                    status=status_str,
                    log_id=rem_log.id if rem_log else None,
                )
            )

        # Sort by due_time
        due_items.sort(key=lambda x: x.due_time)

        return TodayUpcomingRemindersResponse(
            date=t_date,
            total_due=len(due_items),
            completed_count=completed_count,
            pending_count=max(0, len(due_items) - completed_count),
            reminders=due_items,
        )

    async def action_reminder(
        self, user_id: uuid.UUID, reminder_id: uuid.UUID, req: ReminderActionRequest
    ) -> ReminderLog:
        rem = await self.get_reminder_by_id(user_id, reminder_id)
        now = datetime.now(timezone.utc)

        log = ReminderLog(
            reminder_id=rem.id,
            user_id=user_id,
            scheduled_at=now,
            status=req.status,
            completed_at=now if req.status == ReminderStatusEnum.COMPLETED else None,
            notes=req.notes.strip() if req.notes else None,
        )
        self.db.add(log)

        # Dispatch timeline event if marked COMPLETED
        if req.status == ReminderStatusEnum.COMPLETED:
            await self.timeline_service.record_event(
                user_id=user_id,
                category=TimelineCategoryEnum.REMINDER,
                event_type=TimelineEventTypeEnum.REMINDER_COMPLETED,
                title=f"Reminder Completed: {rem.title}",
                summary=f"Completed {rem.title} at {now.strftime('%I:%M %p')}",
                occurred_at=now,
                reference_id=str(rem.id),
                reference_type="reminder",
            )

        await self.db.flush()
        return log

    # ----------------- Notification Preferences -----------------
    async def get_or_create_preferences(self, user_id: uuid.UUID) -> NotificationPreference:
        query = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        result = await self.db.execute(query)
        pref = result.scalar_one_or_none()
        if not pref:
            pref = NotificationPreference(user_id=user_id)
            self.db.add(pref)
            await self.db.flush()
        return pref

    async def update_preferences(
        self, user_id: uuid.UUID, req: NotificationPreferenceUpdateRequest
    ) -> NotificationPreference:
        pref = await self.get_or_create_preferences(user_id)
        if req.enable_in_app is not None:
            pref.enable_in_app = req.enable_in_app
        if req.enable_email is not None:
            pref.enable_email = req.enable_email
        if req.enable_push is not None:
            pref.enable_push = req.enable_push
        if req.medicine_alerts is not None:
            pref.medicine_alerts = req.medicine_alerts
        if req.refill_alerts is not None:
            pref.refill_alerts = req.refill_alerts
        if req.appointment_alerts is not None:
            pref.appointment_alerts = req.appointment_alerts
        if req.wellness_nudges is not None:
            pref.wellness_nudges = req.wellness_nudges
        if req.quiet_hours_start is not None:
            pref.quiet_hours_start = req.quiet_hours_start
        if req.quiet_hours_end is not None:
            pref.quiet_hours_end = req.quiet_hours_end

        await self.db.flush()
        return pref
