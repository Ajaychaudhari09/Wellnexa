import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CitedSourceItem(BaseModel):
    title: str
    source: str

class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    cited_sources: Optional[List[CitedSourceItem]] = []
    disclaimer: Optional[str] = None
    is_safety_triggered: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionCreateRequest(BaseModel):
    title: Optional[str] = Field("Health & Wellness Chat", max_length=200)

class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    is_archived: bool
    messages_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)

class ChatHistoryResponse(BaseModel):
    session_id: uuid.UUID
    title: str
    messages: List[ChatMessageResponse]
