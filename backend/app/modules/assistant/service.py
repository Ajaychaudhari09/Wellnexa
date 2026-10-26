import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.core.exceptions import NotFoundException
from app.models.chat import ChatSession, ChatMessage, ChatRoleEnum
from app.core.encryption import encrypt, decrypt
from app.models.profile import Profile
from app.models.health import Allergy, MedicalCondition, HealthMetric
from app.models.medicine import Medication
from ai.assistant.context_assembler import PatientContextAssembler
from ai.assistant.engine import AIAssistantEngine
from app.modules.assistant.schemas import (
    ChatMessageResponse,
    ChatSessionResponse,
    ChatHistoryResponse,
    CitedSourceItem,
)

class AssistantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, user_id: uuid.UUID, title: Optional[str] = None) -> ChatSession:
        session = ChatSession(
            user_id=user_id,
            title=title.strip() if title else "Health & Wellness Chat",
            is_archived=False,
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_user_sessions(self, user_id: uuid.UUID) -> List[ChatSessionResponse]:
        query = select(ChatSession).where(
            and_(ChatSession.user_id == user_id, ChatSession.is_archived == False)
        ).order_by(desc(ChatSession.updated_at))
        result = await self.db.execute(query)
        sessions = list(result.scalars().all())

        response_list: List[ChatSessionResponse] = []
        for s in sessions:
            cnt_q = select(func.count()).where(ChatMessage.session_id == s.id)
            cnt_res = await self.db.execute(cnt_q)
            msg_count = cnt_res.scalar() or 0
            response_list.append(
                ChatSessionResponse(
                    id=s.id,
                    user_id=s.user_id,
                    title=s.title,
                    is_archived=s.is_archived,
                    messages_count=msg_count,
                    created_at=s.created_at,
                    updated_at=s.updated_at,
                )
            )

        return response_list

    async def get_session_by_id(self, user_id: uuid.UUID, session_id: uuid.UUID) -> ChatSession:
        query = select(ChatSession).where(
            and_(ChatSession.id == session_id, ChatSession.user_id == user_id)
        )
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        if not session:
            raise NotFoundException("ChatSession", session_id)
        return session

    async def build_patient_context(self, user_id: uuid.UUID) -> str:
        # Profile
        prof_res = await self.db.execute(select(Profile).where(Profile.user_id == user_id))
        prof = prof_res.scalar_one_or_none()
        prof_dict = {"gender": prof.gender.value, "blood_group": prof.blood_group.value} if prof else None

        # Medications
        med_res = await self.db.execute(select(Medication).where(and_(Medication.user_id == user_id, Medication.is_active == True)))
        meds = [{"name": m.name, "dosage": m.dosage, "timing": m.timing.value, "is_active": m.is_active} for m in med_res.scalars().all()]

        # Allergies
        alg_res = await self.db.execute(select(Allergy).where(Allergy.user_id == user_id))
        algs = [{"allergen": a.allergen, "severity": a.severity.value} for a in alg_res.scalars().all()]

        # Conditions
        cond_res = await self.db.execute(select(MedicalCondition).where(MedicalCondition.user_id == user_id))
        conds = [{"condition_name": c.condition_name, "status": c.status.value} for c in cond_res.scalars().all()]

        # Recent Metrics
        met_res = await self.db.execute(select(HealthMetric).where(HealthMetric.user_id == user_id).order_by(desc(HealthMetric.recorded_at)).limit(5))
        mets = [{"type": m.metric_type.value, "value": m.value, "unit": m.unit} for m in met_res.scalars().all()]

        return PatientContextAssembler.build_context(
            profile=prof_dict,
            medications=meds,
            allergies=algs,
            conditions=conds,
            recent_metrics=mets,
        )

    async def send_message(self, user_id: uuid.UUID, session_id: uuid.UUID, message_text: str) -> ChatMessageResponse:
        session = await self.get_session_by_id(user_id, session_id)

        # 1. Save User Message
        user_msg = ChatMessage(
            session_id=session.id,
            user_id=user_id,
            role=ChatRoleEnum.USER,
            content=encrypt(message_text.strip()),
            is_safety_triggered=False,
        )
        self.db.add(user_msg)
        await self.db.flush()

        # 2. Build Patient Health Context
        patient_ctx = await self.build_patient_context(user_id)

        # 3. Execute AI Assistant Engine
        ai_result = AIAssistantEngine.process_query(
            user_query=message_text.strip(),
            patient_context=patient_ctx,
        )

        # 4. Save Assistant Response
        assistant_msg = ChatMessage(
            session_id=session.id,
            user_id=user_id,
            role=ChatRoleEnum.ASSISTANT,
            content=encrypt(ai_result["content"]),
            cited_sources=ai_result["cited_sources"],
            disclaimer=ai_result["disclaimer"],
            is_safety_triggered=ai_result["is_safety_triggered"],
        )
        self.db.add(assistant_msg)

        session.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

        cited_items = [CitedSourceItem(**s) for s in (assistant_msg.cited_sources or [])]

        return ChatMessageResponse(
            id=assistant_msg.id,
            session_id=assistant_msg.session_id,
            role=assistant_msg.role.value,
            content=ai_result["content"],
            cited_sources=cited_items,
            disclaimer=assistant_msg.disclaimer,
            is_safety_triggered=assistant_msg.is_safety_triggered,
            created_at=assistant_msg.created_at,
        )

    async def get_session_history(self, user_id: uuid.UUID, session_id: uuid.UUID) -> ChatHistoryResponse:
        session = await self.get_session_by_id(user_id, session_id)
        query = select(ChatMessage).where(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at.asc())
        result = await self.db.execute(query)
        messages = list(result.scalars().all())

        msg_responses = [
            ChatMessageResponse(
                id=m.id,
                session_id=m.session_id,
                role=m.role.value,
                content=decrypt(m.content),
                cited_sources=[CitedSourceItem(**s) for s in (m.cited_sources or [])],
                disclaimer=m.disclaimer,
                is_safety_triggered=m.is_safety_triggered,
                created_at=m.created_at,
            )
            for m in messages
        ]

        return ChatHistoryResponse(
            session_id=session.id,
            title=session.title,
            messages=msg_responses,
        )
