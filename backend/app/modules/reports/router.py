import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.models.report import ReportTypeEnum
from app.modules.reports.schemas import (
    ReportResponse,
    ExtractionItemResponse,
    ConfirmReportRequest,
)
from app.modules.reports.service import OcrService

router = APIRouter(prefix="/reports", tags=["Medical Reports & OCR"])

@router.post("/process-ocr/{document_id}", response_model=ApiResponse[ReportResponse], status_code=status.HTTP_200_OK)
async def process_document_ocr(
    document_id: uuid.UUID,
    report_type: Optional[ReportTypeEnum] = Query(None, description="Optional report panel hint"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ReportResponse]:
    """Run OCR on uploaded document, extract structured clinical fields, and prepare candidate review list."""
    service = OcrService(db)
    report = await service.process_document_ocr(
        user_id=current_user.id,
        document_id=document_id,
        report_type_hint=report_type,
    )

    return ApiResponse[ReportResponse](
        success=True,
        message="OCR processing complete. Please review and confirm extracted fields.",
        data=ReportResponse.model_validate(report),
    )

@router.get("/{report_id}", response_model=ApiResponse[ReportResponse], status_code=status.HTTP_200_OK)
async def get_report_details(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ReportResponse]:
    """Retrieve report extraction items and reference ranges for patient review."""
    service = OcrService(db)
    report = await service.get_report_by_id(current_user.id, report_id)

    return ApiResponse[ReportResponse](
        success=True,
        message="Report details retrieved",
        data=ReportResponse.model_validate(report),
    )

@router.post("/{report_id}/confirm", response_model=ApiResponse[ReportResponse], status_code=status.HTTP_200_OK)
async def confirm_report_extractions(
    report_id: uuid.UUID,
    req: ConfirmReportRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ReportResponse]:
    """Human-in-the-loop confirmation: verify or correct extracted test values and persist to health metrics."""
    service = OcrService(db)
    report = await service.confirm_report(current_user.id, report_id, req)

    return ApiResponse[ReportResponse](
        success=True,
        message="Extracted values confirmed and synchronized with personal health metrics.",
        data=ReportResponse.model_validate(report),
    )

@router.get("", response_model=ApiResponse[List[ReportResponse]], status_code=status.HTTP_200_OK)
async def list_reports(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[ReportResponse]]:
    """List all medical reports for current user."""
    service = OcrService(db)
    reports, _ = await service.list_reports(current_user.id, limit=limit, offset=offset)

    payload = [ReportResponse.model_validate(r) for r in reports]

    return ApiResponse[List[ReportResponse]](
        success=True,
        message="Reports retrieved successfully",
        data=payload,
    )
