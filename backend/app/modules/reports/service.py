import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.core.exceptions import NotFoundException, WellNexaException
from app.models.document import MedicalDocument, DocumentStatusEnum
from app.models.report import (
    MedicalReport,
    ReportExtractionItem,
    ReportTypeEnum,
    ExtractionStatusEnum,
    FlagStatusEnum,
)
from app.models.health import HealthMetric, MetricSourceEnum
from app.models.timeline import TimelineCategoryEnum, TimelineEventTypeEnum
from app.models.audit import AuditLog
from ai.ocr.engine import OCREngine
from ai.ocr.extractor import LabReportExtractor
from ai.ocr.reference_ranges import evaluate_flag
from app.modules.timeline.service import TimelineService
from app.modules.reports.schemas import ConfirmReportRequest

class OcrService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.timeline_service = TimelineService(db)

    async def process_document_ocr(
        self,
        user_id: uuid.UUID,
        document_id: uuid.UUID,
        report_type_hint: Optional[ReportTypeEnum] = None,
    ) -> MedicalReport:
        """Run OCR, extract structured clinical fields, and create pending review items."""
        # 1. Fetch document
        doc_q = select(MedicalDocument).where(
            and_(MedicalDocument.id == document_id, MedicalDocument.user_id == user_id)
        )
        doc_res = await self.db.execute(doc_q)
        doc = doc_res.scalar_one_or_none()
        if not doc:
            raise NotFoundException("MedicalDocument", document_id)

        # Check if already processed
        rep_q = select(MedicalReport).where(MedicalReport.document_id == document_id)
        rep_res = await self.db.execute(rep_q)
        existing_rep = rep_res.scalar_one_or_none()
        if existing_rep:
            return existing_rep

        doc.status = DocumentStatusEnum.PROCESSING_OCR
        await self.db.flush()

        # 2. Extract raw text
        raw_text = OCREngine.extract_text_from_file(doc.file_path, doc.mime_type)

        # 3. Extract structured candidate fields
        extracted_data = LabReportExtractor.extract_fields(raw_text, report_type_hint)
        inferred_type = report_type_hint or LabReportExtractor.infer_report_type(extracted_data, raw_text)

        # 4. Create MedicalReport record
        report = MedicalReport(
            user_id=user_id,
            document_id=document_id,
            report_type=inferred_type,
            status=ExtractionStatusEnum.PENDING_CONFIRMATION,
            raw_text=raw_text,
            summary_notes=f"Extracted {len(extracted_data)} candidate test parameters pending human review.",
        )
        self.db.add(report)
        await self.db.flush()

        # 5. Create ReportExtractionItem records
        for item in extracted_data:
            ext_item = ReportExtractionItem(
                report_id=report.id,
                test_name=item["test_name"],
                metric_type=item["metric_type"],
                detected_value=item["detected_value"],
                confirmed_value=item["confirmed_value"],
                unit=item["unit"],
                reference_range_low=item["reference_range_low"],
                reference_range_high=item["reference_range_high"],
                flag_status=item["flag_status"],
                is_confirmed=False,
                user_corrected=False,
            )
            self.db.add(ext_item)

        doc.status = DocumentStatusEnum.EXTRACTED
        await self.db.flush()

        # Re-fetch with relationships loaded
        q = select(MedicalReport).where(MedicalReport.id == report.id)
        res = await self.db.execute(q)
        return res.scalar_one()

    async def get_report_by_id(self, user_id: uuid.UUID, report_id: uuid.UUID) -> MedicalReport:
        """Fetch report with items ensuring user ownership."""
        query = select(MedicalReport).where(
            and_(MedicalReport.id == report_id, MedicalReport.user_id == user_id)
        )
        result = await self.db.execute(query)
        report = result.scalar_one_or_none()
        if not report:
            raise NotFoundException("MedicalReport", report_id)
        return report

    async def confirm_report(
        self, user_id: uuid.UUID, report_id: uuid.UUID, req: ConfirmReportRequest
    ) -> MedicalReport:
        """Human-in-the-loop confirmation: update values, save to health_metrics, and log to timeline."""
        report = await self.get_report_by_id(user_id, report_id)

        if req.report_date:
            report.report_date = req.report_date
        if req.lab_name:
            report.lab_name = req.lab_name.strip()
        if req.notes:
            report.summary_notes = req.notes.strip()

        # Map confirmed items
        confirm_map = {item.extraction_id: item for item in req.confirmed_items}
        confirmed_metrics_count = 0

        for ext in report.extractions:
            if ext.id in confirm_map:
                c_payload = confirm_map[ext.id]
                if not c_payload.is_confirmed:
                    ext.is_confirmed = False
                    continue

                ext.is_confirmed = True
                ext.confirmed_value = c_payload.confirmed_value
                if round(c_payload.confirmed_value, 2) != round(ext.detected_value, 2):
                    ext.user_corrected = True

                # Re-evaluate flag on confirmed value
                ext.flag_status = evaluate_flag(
                    c_payload.confirmed_value,
                    ext.reference_range_low,
                    ext.reference_range_high,
                )

                # Persist confirmed clinical value to health_metrics
                if ext.metric_type:
                    metric = HealthMetric(
                        user_id=user_id,
                        metric_type=ext.metric_type,
                        value=c_payload.confirmed_value,
                        unit=ext.unit,
                        recorded_at=datetime.now(timezone.utc),
                        source=MetricSourceEnum.OCR_EXTRACTION,
                        notes=f"Confirmed from {report.report_type.value} report",
                        metadata_info={"report_id": str(report.id), "test_name": ext.test_name},
                    )
                    self.db.add(metric)
                    confirmed_metrics_count += 1

        report.status = ExtractionStatusEnum.CONFIRMED
        await self.db.flush()

        # Record confirmation in Health Timeline
        await self.timeline_service.record_event(
            user_id=user_id,
            category=TimelineCategoryEnum.CLINICAL,
            event_type=TimelineEventTypeEnum.METRIC_LOGGED,
            title=f"{report.report_type.value.replace('_', ' ').title()} Confirmed",
            summary=f"Confirmed and logged {confirmed_metrics_count} clinical parameters from lab report.",
            occurred_at=datetime.now(timezone.utc),
            reference_id=str(report.id),
            reference_type="medical_report",
            metadata_info={"report_id": str(report.id), "metrics_synced": confirmed_metrics_count},
        )

        # Audit Log
        audit = AuditLog(
            user_id=user_id,
            action="REPORT_CONFIRMED",
            resource="medical_reports",
            resource_id=str(report.id),
            details={"confirmed_metrics": confirmed_metrics_count, "report_type": report.report_type.value},
        )
        self.db.add(audit)
        await self.db.flush()

        return report

    async def list_reports(
        self, user_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> Tuple[List[MedicalReport], int]:
        """List user's medical reports."""
        query = select(MedicalReport).where(MedicalReport.user_id == user_id)
        count_q = select(func.count()).select_from(query.subquery())
        count_res = await self.db.execute(count_q)
        total = count_res.scalar() or 0

        query = query.order_by(desc(MedicalReport.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        reports = list(result.scalars().all())

        return reports, total
