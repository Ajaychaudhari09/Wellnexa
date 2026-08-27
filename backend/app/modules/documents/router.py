import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.models.document import DocumentCategoryEnum, DocumentStatusEnum
from app.modules.documents.schemas import (
    DocumentResponse,
    DocumentUpdateRequest,
    DocumentListResponse,
)
from app.modules.documents.service import DocumentService

router = APIRouter(prefix="/documents", tags=["Medical Documents & Storage"])

@router.post("/upload", response_model=ApiResponse[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    file: UploadFile = File(..., description="PDF or image file (max 10MB)"),
    category: DocumentCategoryEnum = Form(DocumentCategoryEnum.MEDICAL_REPORT),
    title: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DocumentResponse]:
    """Upload a medical document or prescription with automatic integrity verification and timeline registration."""
    service = DocumentService(db)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    doc = await service.upload_document(
        user_id=current_user.id,
        file=file,
        category=category,
        title=title,
        notes=notes,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    payload = DocumentResponse(
        id=doc.id,
        user_id=doc.user_id,
        category=doc.category.value if hasattr(doc.category, "value") else str(doc.category),
        status=doc.status.value if hasattr(doc.status, "value") else str(doc.status),
        title=doc.title,
        original_file_name=doc.original_file_name,
        file_size_bytes=doc.file_size_bytes,
        mime_type=doc.mime_type,
        checksum_sha256=doc.checksum_sha256,
        uploaded_at=doc.uploaded_at,
        notes=doc.notes,
        metadata_info=doc.metadata_info,
    )

    return ApiResponse[DocumentResponse](
        success=True,
        message="Document uploaded successfully",
        data=payload,
    )

@router.get("", response_model=ApiResponse[DocumentListResponse], status_code=status.HTTP_200_OK)
async def list_documents(
    category: Optional[DocumentCategoryEnum] = Query(None, description="Filter by category"),
    status: Optional[DocumentStatusEnum] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DocumentListResponse]:
    """List medical documents owned by the current authenticated user."""
    service = DocumentService(db)
    docs, total = await service.get_user_documents(
        user_id=current_user.id, category=category, status=status, limit=limit, offset=offset
    )

    payload_items = [
        DocumentResponse(
            id=d.id,
            user_id=d.user_id,
            category=d.category.value if hasattr(d.category, "value") else str(d.category),
            status=d.status.value if hasattr(d.status, "value") else str(d.status),
            title=d.title,
            original_file_name=d.original_file_name,
            file_size_bytes=d.file_size_bytes,
            mime_type=d.mime_type,
            checksum_sha256=d.checksum_sha256,
            uploaded_at=d.uploaded_at,
            notes=d.notes,
            metadata_info=d.metadata_info,
        )
        for d in docs
    ]

    return ApiResponse[DocumentListResponse](
        success=True,
        message="Documents retrieved successfully",
        data=DocumentListResponse(items=payload_items, total_count=total),
    )

@router.get("/{document_id}", response_model=ApiResponse[DocumentResponse], status_code=status.HTTP_200_OK)
async def get_document_metadata(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DocumentResponse]:
    """Retrieve metadata for a specific document."""
    service = DocumentService(db)
    doc = await service.get_document_metadata(current_user.id, document_id)

    payload = DocumentResponse(
        id=doc.id,
        user_id=doc.user_id,
        category=doc.category.value if hasattr(doc.category, "value") else str(doc.category),
        status=doc.status.value if hasattr(doc.status, "value") else str(doc.status),
        title=doc.title,
        original_file_name=doc.original_file_name,
        file_size_bytes=doc.file_size_bytes,
        mime_type=doc.mime_type,
        checksum_sha256=doc.checksum_sha256,
        uploaded_at=doc.uploaded_at,
        notes=doc.notes,
        metadata_info=doc.metadata_info,
    )

    return ApiResponse[DocumentResponse](
        success=True,
        message="Document metadata retrieved",
        data=payload,
    )

@router.get("/{document_id}/download")
async def download_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Stream document binary content securely with attachment disposition."""
    service = DocumentService(db)
    file_path, mime_type, filename = await service.get_document_file_path(current_user.id, document_id)

    return FileResponse(
        path=file_path,
        media_type=mime_type,
        filename=filename,
        content_disposition_type="attachment",
    )

@router.get("/{document_id}/view")
async def view_document_inline(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Stream document content for in-browser or in-app inline rendering."""
    service = DocumentService(db)
    file_path, mime_type, _ = await service.get_document_file_path(current_user.id, document_id)

    return FileResponse(
        path=file_path,
        media_type=mime_type,
        content_disposition_type="inline",
    )

@router.patch("/{document_id}", response_model=ApiResponse[DocumentResponse], status_code=status.HTTP_200_OK)
async def update_document(
    document_id: uuid.UUID,
    req: DocumentUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DocumentResponse]:
    """Update title, category, or notes of an existing document."""
    service = DocumentService(db)
    doc = await service.update_document(current_user.id, document_id, req)

    payload = DocumentResponse(
        id=doc.id,
        user_id=doc.user_id,
        category=doc.category.value if hasattr(doc.category, "value") else str(doc.category),
        status=doc.status.value if hasattr(doc.status, "value") else str(doc.status),
        title=doc.title,
        original_file_name=doc.original_file_name,
        file_size_bytes=doc.file_size_bytes,
        mime_type=doc.mime_type,
        checksum_sha256=doc.checksum_sha256,
        uploaded_at=doc.uploaded_at,
        notes=doc.notes,
        metadata_info=doc.metadata_info,
    )

    return ApiResponse[DocumentResponse](
        success=True,
        message="Document updated successfully",
        data=payload,
    )

@router.delete("/{document_id}", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    """Permanently delete a document record and its underlying stored file."""
    service = DocumentService(db)
    await service.delete_document(current_user.id, document_id)

    return ApiResponse[dict](
        success=True,
        message="Document deleted successfully",
        data={"id": str(document_id)},
    )
