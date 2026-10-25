import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
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
from ai.extraction.report_analyzer import ReportAnalyzer
from app.modules.timeline.service import TimelineService
from app.modules.reports.schemas import (
    ConfirmReportRequest,
    ReportExplanationResponse,
    HistoricalComparisonResponse,
    ParameterComparisonItem,
    ParameterHistoryResponse,
    ParameterHistoryPoint,
)

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
        doc_q = select(MedicalDocument).where(
            and_(MedicalDocument.id == document_id, MedicalDocument.user_id == user_id)
        )
        doc_res = await self.db.execute(doc_q)
        doc = doc_res.scalar_one_or_none()
        if not doc:
            raise NotFoundException("MedicalDocument", document_id)

        rep_q = select(MedicalReport).where(MedicalReport.document_id == document_id)
        rep_res = await self.db.execute(rep_q)
        existing_rep = rep_res.scalar_one_or_none()
        if existing_rep:
            return existing_rep

        doc.status = DocumentStatusEnum.PROCESSING_OCR
        await self.db.flush()

        raw_text = OCREngine.extract_text_from_file(doc.file_path, doc.mime_type)
        extracted_data = LabReportExtractor.extract_fields(raw_text, report_type_hint)
        inferred_type = report_type_hint or LabReportExtractor.infer_report_type(extracted_data, raw_text)

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

        confirm_map = {item.extraction_id: item for item in (req.confirmed_items or [])}
        confirmed_metrics_count = 0

        for ext in report.extractions:
            if not confirm_map or ext.id in confirm_map:
                if ext.id in confirm_map:
                    c_payload = confirm_map[ext.id]
                    if not c_payload.is_confirmed:
                        ext.is_confirmed = False
                        continue
                    final_val = c_payload.confirmed_value
                    if round(c_payload.confirmed_value, 2) != round(ext.detected_value, 2):
                        ext.user_corrected = True
                else:
                    final_val = ext.detected_value

                ext.is_confirmed = True
                ext.confirmed_value = final_val

                ext.flag_status = evaluate_flag(
                    final_val,
                    ext.reference_range_low,
                    ext.reference_range_high,
                )

                if ext.metric_type:
                    metric = HealthMetric(
                        user_id=user_id,
                        metric_type=ext.metric_type,
                        value=final_val,
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

    async def get_report_explanation(self, user_id: uuid.UUID, report_id: uuid.UUID) -> ReportExplanationResponse:
        """Generate educational, plain-language breakdown of report results with safety disclaimers."""
        report = await self.get_report_by_id(user_id, report_id)
        items_dict = [
            {
                "test_name": e.test_name,
                "detected_value": e.detected_value,
                "confirmed_value": e.confirmed_value,
                "unit": e.unit,
                "reference_range_low": e.reference_range_low,
                "reference_range_high": e.reference_range_high,
                "flag_status": e.flag_status.value if hasattr(e.flag_status, "value") else str(e.flag_status),
            }
            for e in report.extractions
        ]

        explanation_data = ReportAnalyzer.generate_explanation(
            report_type=report.report_type.value if hasattr(report.report_type, "value") else str(report.report_type),
            current_items=items_dict,
        )

        return ReportExplanationResponse(**explanation_data)

    async def get_historical_comparison(
        self, user_id: uuid.UUID, report_id: uuid.UUID
    ) -> HistoricalComparisonResponse:
        """Compare current report against the immediately preceding report of the same type."""
        current_report = await self.get_report_by_id(user_id, report_id)

        # Query preceding report of matching type
        prev_q = select(MedicalReport).where(
            and_(
                MedicalReport.user_id == user_id,
                MedicalReport.report_type == current_report.report_type,
                MedicalReport.created_at < current_report.created_at,
                MedicalReport.status == ExtractionStatusEnum.CONFIRMED,
            )
        ).order_by(desc(MedicalReport.created_at)).limit(1)

        prev_res = await self.db.execute(prev_q)
        prev_report = prev_res.scalar_one_or_none()

        if not prev_report or not prev_report.extractions:
            return HistoricalComparisonResponse(
                current_report_id=current_report.id,
                previous_report_id=None,
                report_type=current_report.report_type.value if hasattr(current_report.report_type, "value") else str(current_report.report_type),
                has_previous_report=False,
                parameters_compared=[],
            )

        cur_items = [
            {
                "test_name": e.test_name,
                "detected_value": e.detected_value,
                "confirmed_value": e.confirmed_value,
                "unit": e.unit,
                "flag_status": e.flag_status.value if hasattr(e.flag_status, "value") else str(e.flag_status),
            }
            for e in current_report.extractions
        ]

        prev_items = [
            {
                "test_name": e.test_name,
                "detected_value": e.detected_value,
                "confirmed_value": e.confirmed_value,
                "unit": e.unit,
                "flag_status": e.flag_status.value if hasattr(e.flag_status, "value") else str(e.flag_status),
            }
            for e in prev_report.extractions
        ]

        raw_comparisons = ReportAnalyzer.compare_reports(cur_items, prev_items)
        compared_items = [ParameterComparisonItem(**c) for c in raw_comparisons]

        return HistoricalComparisonResponse(
            current_report_id=current_report.id,
            previous_report_id=prev_report.id,
            report_type=current_report.report_type.value if hasattr(current_report.report_type, "value") else str(current_report.report_type),
            has_previous_report=True,
            parameters_compared=compared_items,
        )

    async def get_parameter_history(
        self, user_id: uuid.UUID, test_name: str
    ) -> ParameterHistoryResponse:
        """Fetch historical points for a specific lab parameter across all reports."""
        query = select(ReportExtractionItem, MedicalReport).join(
            MedicalReport, ReportExtractionItem.report_id == MedicalReport.id
        ).where(
            and_(
                MedicalReport.user_id == user_id,
                func.lower(ReportExtractionItem.test_name) == test_name.lower().strip(),
            )
        ).order_by(MedicalReport.created_at.asc())

        result = await self.db.execute(query)
        rows = result.all()

        points: List[ParameterHistoryPoint] = []
        unit = ""
        for ext, rep in rows:
            val = ext.confirmed_value if ext.confirmed_value is not None else ext.detected_value
            unit = ext.unit
            points.append(
                ParameterHistoryPoint(
                    report_id=rep.id,
                    report_date=rep.report_date,
                    created_at=rep.created_at,
                    value=val,
                    unit=ext.unit,
                    flag_status=ext.flag_status.value if hasattr(ext.flag_status, "value") else str(ext.flag_status),
                )
            )

        return ParameterHistoryResponse(
            test_name=test_name,
            unit=unit,
            data_points=points,
        )

    async def list_reports(
        self, user_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> Tuple[List[MedicalReport], int]:
        query = select(MedicalReport).where(MedicalReport.user_id == user_id)
        count_q = select(func.count()).select_from(query.subquery())
        count_res = await self.db.execute(count_q)
        total = count_res.scalar() or 0

        query = query.order_by(desc(MedicalReport.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        reports = list(result.scalars().all())

        return reports, total
