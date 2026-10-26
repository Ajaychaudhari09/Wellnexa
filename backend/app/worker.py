"""Background worker: asyncio loop, no extra scheduler framework."""
import asyncio
import logging
import os
from datetime import datetime, timezone, time
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.email_service import send_email
from app.models.reminder import Reminder
from app.models.notification import Notification
from app.models.user import User
from app.models.reminder import NotificationPreference

POLL_SECONDS = int(os.getenv("WORKER_POLL_SECONDS", "60"))
logger = logging.getLogger("wellnexa.worker")


async def process_due_reminders():
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(Reminder).where(Reminder.is_active.is_(True)).with_for_update(skip_locked=True)
        )
        reminders = result.scalars().all()
        for r in reminders:
            if r.recurrence.value == "ONCE" and r.due_date:
                if r.due_date != now.date():
                    continue
            elif r.due_date and r.due_date > now.date():
                continue
            try:
                hh, mm = (int(x) for x in r.due_time.split(":", 1))
                due_at = datetime.combine(now.date(), time(hh, mm), tzinfo=timezone.utc)
            except (ValueError, TypeError):
                continue
            if due_at > now or (r.recurrence.value == "ONCE" and r.due_date is None):
                continue

            pref_result = await db.execute(select(NotificationPreference).where(NotificationPreference.user_id == r.user_id))
            pref = pref_result.scalar_one_or_none()
            if pref and not pref.enable_in_app and not pref.enable_email:
                continue
            # Add the dashboard notification once per due date. A row lock prevents
            # two worker processes from claiming the same reminder concurrently.
            existing = await db.execute(select(Notification.id).where(
                Notification.user_id == r.user_id,
                Notification.reference_id == f"{r.id}:{now.date().isoformat()}"
            ).limit(1))
            if existing.scalar_one_or_none():
                continue
            if not pref or pref.enable_in_app:
                db.add(Notification(
                    user_id=r.user_id,
                    title="WellNexa reminder",
                    body="You have a WellNexa reminder. Log in to view details.",
                    action_url="/dashboard",
                    reference_id=f"{r.id}:{now.date().isoformat()}",
                    reference_type="reminder",
                    is_read=False,
                ))
            if pref and pref.enable_email:
                user_result = await db.execute(select(User).where(User.id == r.user_id))
                user = user_result.scalar_one_or_none()
                if user:
                    # Email body deliberately contains no reminder details.
                    sent = await asyncio.to_thread(send_email, user.email, "WellNexa reminder", "You have a WellNexa reminder. Log in to view details.\n\nhttp://localhost:3000/dashboard")
                    if not sent:
                        raise RuntimeError("Reminder email delivery failed")
        await db.commit()


async def process_due_reminders_once():
    """Process one due reminder cycle; exposed for focused integration tests."""
    await process_due_reminders()


async def main():
    logger.info("Worker started")
    while True:
        try:
            await process_due_reminders()
        except Exception:
            # Avoid logging exception strings that could contain email addresses,
            # SQL parameters, or health record content.
            logger.exception("Worker cycle failed")
        await asyncio.sleep(POLL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
