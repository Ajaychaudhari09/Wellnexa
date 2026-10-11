import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.modules.assistant.schemas import (
    ChatSessionCreateRequest,
    ChatSessionResponse,
    SendMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
)
from app.modules.assistant.service import AssistantService

router = APIRouter(prefix="/assistant", tags=["AI Health Assistant"])

@router.post("/sessions", response_model=ApiResponse[ChatSessionResponse], status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    req: ChatSessionCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ChatSessionResponse]:
    """Create a new conversational chat session."""
    service = AssistantService(db)
    session = await service.create_session(current_user.id, title=req.title)
    payload = ChatSessionResponse(
        id=session.id,
        user_id=session.user_id,
        title=session.title,
        is_archived=session.is_archived,
        messages_count=0,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )
    return ApiResponse[ChatSessionResponse](success=True, message="Chat session created", data=payload)

@router.get("/sessions", response_model=ApiResponse[List[ChatSessionResponse]], status_code=status.HTTP_200_OK)
async def list_chat_sessions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[ChatSessionResponse]]:
    """List all active chat sessions for the patient."""
    service = AssistantService(db)
    sessions = await service.get_user_sessions(current_user.id)
    return ApiResponse[List[ChatSessionResponse]](success=True, message="Sessions retrieved", data=sessions)

@router.post("/sessions/{session_id}/messages", response_model=ApiResponse[ChatMessageResponse], status_code=status.HTTP_200_OK)
async def send_chat_message(
    session_id: uuid.UUID,
    req: SendMessageRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ChatMessageResponse]:
    """Send health inquiry to AI Assistant, returning evidence-grounded response with RAG citations."""
    service = AssistantService(db)
    response_msg = await service.send_message(current_user.id, session_id, req.message)
    return ApiResponse[ChatMessageResponse](success=True, message="Response generated", data=response_msg)

@router.get("/sessions/{session_id}/messages", response_model=ApiResponse[ChatHistoryResponse], status_code=status.HTTP_200_OK)
async def get_session_history(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ChatHistoryResponse]:
    """Retrieve full message history for a chat session."""
    service = AssistantService(db)
    history = await service.get_session_history(current_user.id, session_id)
    return ApiResponse[ChatHistoryResponse](success=True, message="History retrieved", data=history)
