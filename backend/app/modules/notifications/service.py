import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func, update

from app.core.exceptions import NotFoundException, WellNexaException
from app.models.notification import (
    Notification,
    NotificationTypeEnum,
    NotificationPriorityEnum,
)
from app.models.reminder import NotificationPreference
from app.modules.notifications.schemas import (
    SendNotificationRequest,
    NotificationResponse,
)

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def dispatch_notification(self, user_id: uuid.UUID, req: SendNotificationRequest) -> Notification:
        # Check preferences
        pref_q = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        pref_res = await self.db.execute(pref_q)
        pref = pref_res.scalar_one_or_none()

        if pref:
            # Check specific alert toggles
            if req.notification_type == NotificationTypeEnum.MEDICINE_DUE and not pref.medicine_alerts:
                pass # Can still store in in-app
            elif req.notification_type == NotificationTypeEnum.REFILL_ALERT and not pref.refill_alerts:
                pass
            elif req.notification_type == NotificationTypeEnum.APPOINTMENT_UPCOMING and not pref.appointment_alerts:
                pass

        notification = Notification(
            user_id=user_id,
            notification_type=req.notification_type,
            title=req.title.strip(),
            body=req.body.strip(),
            is_read=False,
            action_url=req.action_url,
            reference_id=req.reference_id,
            reference_type=req.reference_type,
            priority=req.priority,
        )
        self.db.add(notification)
        await self.db.flush()

        # Multi-Channel Dispatch Abstraction (Push Notification / Email simulation)
        print(f"[Notification Dispatcher] Sent {req.priority.value} alert '{req.title}' to user {user_id} (Channels: In-App, Push={pref.enable_push if pref else True}, Email={pref.enable_email if pref else False})")

        return notification

    async def get_user_notifications(
        self, user_id: uuid.UUID, is_read: Optional[bool] = None, limit: int = 50, offset: int = 0
    ) -> List[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)
        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
        query = query.order_by(desc(Notification.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        query = select(func.count()).select_from(Notification).where(
            and_(Notification.user_id == user_id, Notification.is_read == False)
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def mark_as_read(self, user_id: uuid.UUID, notification_id: uuid.UUID) -> Notification:
        query = select(Notification).where(
            and_(Notification.id == notification_id, Notification.user_id == user_id)
        )
        result = await self.db.execute(query)
        notif = result.scalar_one_or_none()
        if not notif:
            raise NotFoundException("Notification", notification_id)

        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
        await self.db.flush()
        return notif

    async def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        now = datetime.now(timezone.utc)
        stmt = update(Notification).where(
            and_(Notification.user_id == user_id, Notification.is_read == False)
        ).values(is_read=True, read_at=now)
        res = await self.db.execute(stmt)
        await self.db.flush()
        return res.rowcount
