import uuid
from datetime import datetime, date, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.models.audit import AuditLog
from app.modules.audit.schemas import (
    AuditLogResponse,
    PatientActivityItem,
    PatientActivitySummaryResponse,
    AdminAuditLogListResponse,
)

ACTION_LABELS = {
    "USER_REGISTERED": "Account Registered",
    "USER_LOGIN": "Successful Login",
    "USER_LOGOUT": "User Logout",
    "DOCUMENT_UPLOADED": "Medical Document Uploaded",
    "DOCUMENT_VIEWED": "Document Previewed",
    "DOCUMENT_DOWNLOADED": "Document Downloaded",
    "REPORT_CONFIRMED": "Lab Report Confirmed",
    "MEDICATION_ADDED": "New Medication Added",
    "DOCTOR_ACCESS_GRANTED": "Doctor Access Grant Created",
    "DOCTOR_ACCESS_REVOKED": "Doctor Access Grant Revoked",
    "EXPORT_HEALTH_DATA": "Health Record Exported",
    "CONSENT_UPDATED": "Consent Preferences Updated",
}

class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_audit_event(
        self,
        user_id: Optional[uuid.UUID],
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Write immutable audit entry."""
        log = AuditLog(
            user_id=user_id,
            action=action.strip(),
            resource=resource.strip(),
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def get_patient_activity_stream(self, user_id: uuid.UUID, limit: int = 50) -> PatientActivitySummaryResponse:
        """User-friendly security and access log for patient review."""
        query = select(AuditLog).where(AuditLog.user_id == user_id).order_by(desc(AuditLog.created_at)).limit(limit)
        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        items: List[PatientActivityItem] = []
        for l in logs:
            action_label = ACTION_LABELS.get(l.action, l.action.replace("_", " ").title())
            desc_text = f"Activity on {l.resource}"
            if l.details:
                if "report_type" in l.details:
                    desc_text = f"Confirmed {l.details['report_type']} report"
                elif "name" in l.details:
                    desc_text = f"Added {l.details['name']}"

            items.append(
                PatientActivityItem(
                    id=l.id,
                    action_label=action_label,
                    description=desc_text,
                    resource_type=l.resource,
                    ip_address=l.ip_address,
                    timestamp=l.created_at,
                )
            )

        return PatientActivitySummaryResponse(
            user_id=user_id,
            total_events=len(items),
            activities=items,
        )

    async def query_admin_audit_logs(
        self,
        user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AdminAuditLogListResponse:
        """Admin compliance audit search and filtering."""
        query = select(AuditLog)

        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action.strip())
        if resource:
            query = query.where(AuditLog.resource == resource.strip())
        if start_date:
            query = query.where(func.date(AuditLog.created_at) >= start_date)
        if end_date:
            query = query.where(func.date(AuditLog.created_at) <= end_date)

        # Count total
        count_q = select(func.count()).select_from(query.subquery())
        count_res = await self.db.execute(count_q)
        total_count = count_res.scalar() or 0

        # Paginate
        query = query.order_by(desc(AuditLog.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return AdminAuditLogListResponse(
            total_count=total_count,
            limit=limit,
            offset=offset,
            logs=[AuditLogResponse.model_validate(l) for l in logs],
        )
