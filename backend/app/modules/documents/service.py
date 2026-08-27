import hashlib
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.core.config import settings
from app.core.exceptions import WellNexaException, NotFoundException, ForbiddenException
from app.models.document import MedicalDocument, DocumentCategoryEnum, DocumentStatusEnum
from app.models.timeline import TimelineCategoryEnum, TimelineEventTypeEnum
from app.models.audit import AuditLog
from app.modules.timeline.service import TimelineService
from app.modules.documents.schemas import DocumentUpdateRequest

ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.timeline_service = TimelineService(db)

    async def upload_document(
        self,
        user_id: uuid.UUID,
        file: UploadFile,
        category: DocumentCategoryEnum = DocumentCategoryEnum.MEDICAL_REPORT,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> MedicalDocument:
        """Validate, hash, store to disk, persist metadata, and dispatch timeline event."""
        # 1. Validate MIME type
        content_type = file.content_type or "application/octet-stream"
        if content_type not in ALLOWED_MIME_TYPES:
            raise WellNexaException(
                status_code=400,
                detail=f"Unsupported file format '{content_type}'. Allowed types: PDF, JPEG, PNG, WEBP.",
            )

        # 2. Read content & validate size
        content = await file.read()
        file_size = len(content)
        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            raise WellNexaException(
                status_code=400,
                detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB.",
            )
        if file_size == 0:
            raise WellNexaException(status_code=400, detail="Uploaded file cannot be empty.")

        # 3. Compute SHA-256 checksum
        checksum_sha256 = hashlib.sha256(content).hexdigest()

        # 4. Generate secure storage path
        ext = ALLOWED_MIME_TYPES[content_type]
        doc_uuid = uuid.uuid4()
        internal_file_name = f"{doc_uuid}{ext}"
        
        user_storage_dir = os.path.join(settings.UPLOAD_DIR, str(user_id))
        os.makedirs(user_storage_dir, exist_ok=True)
        file_path = os.path.join(user_storage_dir, internal_file_name)

        # Save to disk
        with open(file_path, "wb") as f:
            f.write(content)

        # 5. Determine title
        doc_title = title.strip() if title and title.strip() else (file.filename or "Uploaded Document")

        # 6. Create database record
        doc = MedicalDocument(
            id=doc_uuid,
            user_id=user_id,
            category=category,
            status=DocumentStatusEnum.UPLOADED,
            title=doc_title,
            file_name=internal_file_name,
            original_file_name=file.filename or internal_file_name,
            file_size_bytes=file_size,
            mime_type=content_type,
            file_path=file_path,
            checksum_sha256=checksum_sha256,
            notes=notes.strip() if notes else None,
            metadata_info={"original_filename": file.filename, "size_kb": round(file_size / 1024, 2)},
        )
        self.db.add(doc)
        await self.db.flush()

        # 7. Auto-emit Health Timeline event
        t_event_type = (
            TimelineEventTypeEnum.REPORT_UPLOADED
            if category == DocumentCategoryEnum.MEDICAL_REPORT
            else (TimelineEventTypeEnum.PRESCRIPTION_ADDED if category == DocumentCategoryEnum.PRESCRIPTION else TimelineEventTypeEnum.SYSTEM_NOTICE)
        )
        t_category = TimelineCategoryEnum.CLINICAL if category in (DocumentCategoryEnum.MEDICAL_REPORT, DocumentCategoryEnum.PRESCRIPTION) else TimelineCategoryEnum.GENERAL

        await self.timeline_service.record_event(
            user_id=user_id,
            category=t_category,
            event_type=t_event_type,
            title=f"{category.value.replace('_', ' ').title()} Uploaded",
            summary=f"Document '{doc_title}' ({round(file_size / 1024, 1)} KB) successfully uploaded.",
            occurred_at=doc.uploaded_at,
            reference_id=str(doc.id),
            reference_type="medical_document",
            metadata_info={"document_id": str(doc.id), "category": category.value},
        )

        # 8. Create Audit Log
        audit = AuditLog(
            user_id=user_id,
            action="DOCUMENT_UPLOADED",
            resource="medical_documents",
            resource_id=str(doc.id),
            ip_address=ip_address,
            user_agent=user_agent,
            details={"title": doc.title, "category": category.value, "size_bytes": file_size},
        )
        self.db.add(audit)
        await self.db.flush()

        return doc

    async def get_user_documents(
        self,
        user_id: uuid.UUID,
        category: Optional[DocumentCategoryEnum] = None,
        status: Optional[DocumentStatusEnum] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[MedicalDocument], int]:
        """List documents owned by the user."""
        query = select(MedicalDocument).where(MedicalDocument.user_id == user_id)
        if category:
            query = query.where(MedicalDocument.category == category)
        if status:
            query = query.where(MedicalDocument.status == status)

        count_q = select(func.count()).select_from(query.subquery())
        count_res = await self.db.execute(count_q)
        total = count_res.scalar() or 0

        query = query.order_by(desc(MedicalDocument.uploaded_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        docs = list(result.scalars().all())

        return docs, total

    async def get_document_metadata(self, user_id: uuid.UUID, document_id: uuid.UUID) -> MedicalDocument:
        """Fetch document metadata ensuring user ownership."""
        query = select(MedicalDocument).where(
            and_(MedicalDocument.id == document_id, MedicalDocument.user_id == user_id)
        )
        result = await self.db.execute(query)
        doc = result.scalar_one_or_none()
        if not doc:
            raise NotFoundException("MedicalDocument", document_id)
        return doc

    async def get_document_file_path(self, user_id: uuid.UUID, document_id: uuid.UUID) -> Tuple[str, str, str]:
        """Return (file_path, mime_type, original_file_name) verifying ownership."""
        doc = await self.get_document_metadata(user_id, document_id)
        if not os.path.exists(doc.file_path):
            raise NotFoundException("Physical document file", document_id)
        return doc.file_path, doc.mime_type, doc.original_file_name

    async def update_document(
        self, user_id: uuid.UUID, document_id: uuid.UUID, req: DocumentUpdateRequest
    ) -> MedicalDocument:
        """Update title, category, or notes."""
        doc = await self.get_document_metadata(user_id, document_id)
        if req.title is not None:
            doc.title = req.title.strip()
        if req.category is not None:
            doc.category = req.category
        if req.notes is not None:
            doc.notes = req.notes.strip()
        await self.db.flush()
        return doc

    async def delete_document(self, user_id: uuid.UUID, document_id: uuid.UUID) -> None:
        """Delete database record and remove file from disk."""
        doc = await self.get_document_metadata(user_id, document_id)
        
        # Remove physical file
        if os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except OSError:
                pass

        await self.db.delete(doc)
        await self.db.flush()

        # Audit log
        audit = AuditLog(
            user_id=user_id,
            action="DOCUMENT_DELETED",
            resource="medical_documents",
            resource_id=str(document_id),
        )
        self.db.add(audit)
        await self.db.flush()
