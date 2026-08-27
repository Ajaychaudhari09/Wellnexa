import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.document import DocumentCategoryEnum, DocumentStatusEnum

class DocumentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    category: str
    status: str
    title: str
    original_file_name: str
    file_size_bytes: int
    mime_type: str
    checksum_sha256: str
    uploaded_at: datetime
    notes: Optional[str] = None
    metadata_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[DocumentCategoryEnum] = None
    notes: Optional[str] = Field(None, max_length=500)

class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total_count: int
