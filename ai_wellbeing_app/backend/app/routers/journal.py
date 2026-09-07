from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from app.database import get_db
from app.models.user import UserModel
from app.models.journal import JournalEntryModel
from app.schemas.journal import (
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryResponse,
    JournalPromptSuggestion
)
from app.routers.auth import get_current_user_optional

router = APIRouter(prefix="/api/journal", tags=["Private Journal"])

DEFAULT_PROMPTS = [
    {
        "id": "p1",
        "category": "Emotional Release",
        "prompt_text": "What is one thing that has been taking up too much room in your mind today?"
    },
    {
        "id": "p2",
        "category": "Self-Compassion",
        "prompt_text": "If a close friend were going through what you're dealing with, what kind words would you say to them?"
    },
    {
        "id": "p3",
        "category": "Grounding",
        "prompt_text": "Name three small things in your environment or daily life that brought you a sense of comfort recently."
    },
    {
        "id": "p4",
        "category": "Boundaries",
        "prompt_text": "What is something you wish you could say 'no' to right now to protect your peace?"
    },
    {
        "id": "p5",
        "category": "Looking Forward",
        "prompt_text": "What is one small, gentle thing you are looking forward to in the coming days?"
    }
]

@router.get("/prompts", response_model=List[JournalPromptSuggestion])
async def get_prompt_suggestions():
    """Retrieve gentle journaling prompts for reflection."""
    return [JournalPromptSuggestion(**p) for p in DEFAULT_PROMPTS]

@router.post("", response_model=JournalEntryResponse)
async def create_journal_entry(
    data: JournalEntryCreate,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Save a private journal reflection isolated to user account."""
    user_id = current_user.id if current_user else None
    entry = JournalEntryModel(
        id=str(uuid.uuid4()),
        user_id=user_id,
        session_id=data.session_id,
        title=data.title or "My Reflection",
        content=data.content,
        prompt_used=data.prompt_used,
        emotion_tag=data.emotion_tag
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return JournalEntryResponse.model_validate(entry)

@router.get("", response_model=List[JournalEntryResponse])
async def list_journal_entries(
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """List private journal entries for the current user."""
    user_id = current_user.id if current_user else None
    stmt = select(JournalEntryModel)
    if user_id:
        stmt = stmt.where(JournalEntryModel.user_id == user_id)
    else:
        stmt = stmt.where(JournalEntryModel.user_id == None)
    
    stmt = stmt.order_by(desc(JournalEntryModel.created_at))
    result = await db.execute(stmt)
    entries = result.scalars().all()
    return [JournalEntryResponse.model_validate(e) for e in entries]

@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: str,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Fetch a specific journal entry."""
    stmt = select(JournalEntryModel).where(JournalEntryModel.id == entry_id)
    if current_user:
        stmt = stmt.where((JournalEntryModel.user_id == current_user.id) | (JournalEntryModel.user_id == None))
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return JournalEntryResponse.model_validate(entry)

@router.put("/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: str,
    data: JournalEntryUpdate,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Update a journal entry."""
    stmt = select(JournalEntryModel).where(JournalEntryModel.id == entry_id)
    if current_user:
        stmt = stmt.where((JournalEntryModel.user_id == current_user.id) | (JournalEntryModel.user_id == None))
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    if data.title is not None:
        entry.title = data.title
    if data.content is not None:
        entry.content = data.content
    if data.emotion_tag is not None:
        entry.emotion_tag = data.emotion_tag
    entry.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(entry)
    return JournalEntryResponse.model_validate(entry)

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal_entry(
    entry_id: str,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Delete a journal entry."""
    stmt = select(JournalEntryModel).where(JournalEntryModel.id == entry_id)
    if current_user:
        stmt = stmt.where((JournalEntryModel.user_id == current_user.id) | (JournalEntryModel.user_id == None))
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    await db.delete(entry)
    await db.commit()
    return None
