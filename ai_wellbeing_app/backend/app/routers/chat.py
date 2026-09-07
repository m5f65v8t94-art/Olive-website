from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, desc
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from app.database import get_db
from app.models.user import UserModel
from app.models.session import SessionModel
from app.models.message import MessageModel
from app.schemas.mode import ModeInfo, ConversationModeEnum
from app.schemas.chat import (
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatTurnRequest,
    ChatTurnResponse
)
from app.utils.constants import CONVERSATION_MODES, NON_CLINICAL_DISCLAIMER
from app.services import get_ai_provider, safety_service, continuity_service
from app.routers.auth import get_current_user_optional, get_current_user

router = APIRouter(prefix="/api/chat", tags=["Chat & Modes"])

@router.get("/modes", response_model=List[ModeInfo])
async def get_modes():
    """Retrieve details and guidelines for the 4 conversation modes."""
    modes = []
    for mode_id, info in CONVERSATION_MODES.items():
        modes.append(ModeInfo(
            id=ConversationModeEnum(info["id"]),
            title=info["title"],
            icon=info["icon"],
            short_description=info["short_description"],
            prompt_guideline=info["prompt_guideline"]
        ))
    return modes

@router.post("/turn", response_model=ChatTurnResponse)
async def chat_turn(
    request: ChatTurnRequest,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Main interactive chat turn endpoint.
    Performs safety screening, AI generation in the selected mode, context tracking, and storage.
    Guarantees exactly one response per user message.
    """
    user_id = current_user.id if current_user else None

    # 1. Resolve or Create Session
    session = None
    if request.session_id:
        stmt = select(SessionModel).where(SessionModel.id == request.session_id)
        if user_id:
            stmt = stmt.where((SessionModel.user_id == user_id) | (SessionModel.user_id == None))
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

    if not session:
        session = SessionModel(
            id=request.session_id or str(uuid.uuid4()),
            user_id=user_id,
            title=request.message[:40] if len(request.message) > 40 else request.message,
            current_mode=request.mode.value
        )
        db.add(session)
        await db.flush()
    else:
        if user_id and not session.user_id:
            session.user_id = user_id
        session.current_mode = request.mode.value
        session.updated_at = datetime.now(timezone.utc)

    # 2. Fetch past messages for context & state analysis
    hist_stmt = (
        select(MessageModel)
        .where(MessageModel.session_id == session.id)
        .order_by(MessageModel.timestamp.asc())
    )
    hist_result = await db.execute(hist_stmt)
    past_msgs = hist_result.scalars().all()
    history_dicts = [{"role": m.role, "content": m.content} for m in past_msgs]

    # 3. State-Aware Safety Assessment
    safety = safety_service.assess_message(request.message, history=history_dicts)

    # 4. Store User Message
    user_msg = MessageModel(
        session_id=session.id,
        role="user",
        content=request.message,
        mode=request.mode.value,
        is_safety_flagged=safety.is_crisis or (safety.safety_state in ["immediate_escalation", "initial_disclosure", "safe_but_reluctant"])
    )
    db.add(user_msg)
    await db.flush()

    # 5. Generate AI Response
    if safety.support_message:
        ai_content = safety.support_message
    else:
        ai_provider = get_ai_provider()
        ai_content = await ai_provider.generate_response(
            mode=request.mode.value,
            user_message=request.message,
            conversation_history=history_dicts,
            context_summary=session.context_summary
        )

        new_summary = continuity_service.update_context_summary(
            session.context_summary,
            history_dicts + [{"role": "user", "content": request.message}]
        )
        session.context_summary = new_summary

    # 6. Store Assistant Message (Strictly one assistant message per turn)
    assistant_msg = MessageModel(
        session_id=session.id,
        role="assistant",
        content=ai_content,
        mode=request.mode.value,
        is_safety_flagged=safety.is_crisis or (safety.safety_state in ["immediate_escalation", "initial_disclosure", "safe_but_reluctant"])
    )
    db.add(assistant_msg)
    await db.commit()

    return ChatTurnResponse(
        session_id=session.id,
        user_message=ChatMessageResponse.model_validate(user_msg),
        assistant_message=ChatMessageResponse.model_validate(assistant_msg),
        current_mode=request.mode,
        safety_assessment=safety
    )

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_sessions(
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """List conversation sessions for history views (filtered per user)."""
    user_id = current_user.id if current_user else None
    stmt = select(SessionModel).where(SessionModel.is_archived == False)
    if user_id:
        stmt = stmt.where(SessionModel.user_id == user_id)
    else:
        # For guest sessions without auth
        stmt = stmt.where(SessionModel.user_id == None)
    
    stmt = stmt.order_by(desc(SessionModel.updated_at))
    result = await db.execute(stmt)
    sessions = result.scalars().all()

    response_list = []
    for s in sessions:
        msg_stmt = (
            select(MessageModel)
            .where(MessageModel.session_id == s.id)
            .order_by(desc(MessageModel.timestamp))
        )
        msg_result = await db.execute(msg_stmt)
        msgs = msg_result.scalars().all()
        preview = msgs[0].content[:80] + "..." if msgs else None
        
        response_list.append(ChatSessionResponse(
            id=s.id,
            title=s.title or "Conversation",
            current_mode=s.current_mode,
            context_summary=s.context_summary,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=len(msgs),
            latest_message_preview=preview
        ))
    return response_list

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    data: ChatSessionCreate,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Create a new empty conversation session."""
    user_id = current_user.id if current_user else None
    session = SessionModel(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=data.title or "New Conversation",
        current_mode=data.initial_mode.value if data.initial_mode else "just_listen"
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        current_mode=session.current_mode,
        context_summary=session.context_summary,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0,
        latest_message_preview=None
    )

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: str,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Fetch all messages for a specific conversation session."""
    stmt = (
        select(MessageModel)
        .where(MessageModel.session_id == session_id)
        .order_by(MessageModel.timestamp.asc())
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return [ChatMessageResponse.model_validate(m) for m in messages]

@router.patch("/sessions/{session_id}", response_model=ChatSessionResponse)
@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_session(
    session_id: str,
    data: ChatSessionUpdate,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Update conversation session title (rename without redirecting)."""
    stmt = select(SessionModel).where(SessionModel.id == session_id)
    if current_user:
        stmt = stmt.where((SessionModel.user_id == current_user.id) | (SessionModel.user_id == None))
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.title = data.title.strip()
    session.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)
    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        current_mode=session.current_mode,
        context_summary=session.context_summary,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0,
        latest_message_preview=None
    )

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Delete an individual conversation session and all its messages."""
    stmt = select(SessionModel).where(SessionModel.id == session_id)
    if current_user:
        stmt = stmt.where((SessionModel.user_id == current_user.id) | (SessionModel.user_id == None))
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(session)
    await db.commit()
    return None

@router.delete("/sessions", status_code=status.HTTP_204_NO_CONTENT)
async def purge_all_sessions(
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Wipe conversation history for complete privacy."""
    if current_user:
        stmt = select(SessionModel).where(SessionModel.user_id == current_user.id)
        result = await db.execute(stmt)
        sessions = result.scalars().all()
        for s in sessions:
            await db.delete(s)
    else:
        await db.execute(delete(MessageModel))
        await db.execute(delete(SessionModel))
    await db.commit()
    return None
