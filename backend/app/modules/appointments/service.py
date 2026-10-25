import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.appointment import Appointment, AppointmentStatusEnum
from app.models.timeline import HealthTimelineEvent, TimelineCategoryEnum, TimelineEventTypeEnum
from app.models.reminder import Reminder, ReminderTypeEnum, RecurrenceTypeEnum
from app.modules.appointments.schemas import AppointmentCreateRequest, AppointmentUpdateRequest
from app.core.exceptions import NotFoundException

class AppointmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_appointment(self, user_id: uuid.UUID, req: AppointmentCreateRequest) -> Appointment:
        appointment = Appointment(
            user_id=user_id,
            doctor_name=req.doctor_name,
            specialty=req.specialty,
            clinic_or_hospital=req.clinic_or_hospital,
            location=req.location,
            appointment_date=req.appointment_date,
            appointment_time=req.appointment_time,
            purpose=req.purpose,
            notes=req.notes,
            status=AppointmentStatusEnum.SCHEDULED,
            appointment_type=req.appointment_type,
        )
        self.db.add(appointment)
        await self.db.flush()

        # Automatically register a health timeline event
        timeline_event = HealthTimelineEvent(
            user_id=user_id,
            category=TimelineCategoryEnum.APPOINTMENT,
            event_type=TimelineEventTypeEnum.APPOINTMENT_SCHEDULED,
            title=f"Appointment Scheduled: {req.doctor_name} ({req.specialty})",
            summary=f"Scheduled for {req.appointment_date} at {req.appointment_time} • Purpose: {req.purpose}",
            occurred_at=datetime.now(timezone.utc),
        )
        self.db.add(timeline_event)

        # Automatically schedule a smart reminder
        reminder = Reminder(
            user_id=user_id,
            reminder_type=ReminderTypeEnum.APPOINTMENT,
            title=f"Consultation with {req.doctor_name}",
            description=f"{req.specialty} at {req.clinic_or_hospital or req.location or 'Clinic'}",
            due_time=req.appointment_time,
            due_date=req.appointment_date,
            recurrence=RecurrenceTypeEnum.ONCE,
        )
        self.db.add(reminder)

        await self.db.commit()
        await self.db.refresh(appointment)
        return appointment

    async def get_user_appointments(self, user_id: uuid.UUID) -> List[Appointment]:
        query = select(Appointment).where(Appointment.user_id == user_id).order_by(Appointment.appointment_date.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_appointment(self, user_id: uuid.UUID, appointment_id: uuid.UUID, req: AppointmentUpdateRequest) -> Appointment:
        query = select(Appointment).where(Appointment.id == appointment_id, Appointment.user_id == user_id)
        result = await self.db.execute(query)
        appointment = result.scalar_one_or_none()
        if not appointment:
            raise NotFoundException("Appointment not found")

        update_data = req.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(appointment, key, val)

        await self.db.commit()
        await self.db.refresh(appointment)
        return appointment

    async def cancel_appointment(self, user_id: uuid.UUID, appointment_id: uuid.UUID) -> Appointment:
        query = select(Appointment).where(Appointment.id == appointment_id, Appointment.user_id == user_id)
        result = await self.db.execute(query)
        appointment = result.scalar_one_or_none()
        if not appointment:
            raise NotFoundException("Appointment not found")

        appointment.status = AppointmentStatusEnum.CANCELLED
        await self.db.commit()
        await self.db.refresh(appointment)
        return appointment
