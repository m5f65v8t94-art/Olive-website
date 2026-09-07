from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
import uuid
from collections import Counter

from app.database import get_db
from app.models.user import UserModel
from app.models.mood import MoodLogModel
from app.schemas.mood import MoodLogCreate, MoodLogResponse, MoodSummaryResponse
from app.routers.auth import get_current_user_optional

router = APIRouter(prefix="/api/mood", tags=["Feelings Check-in"])

@router.post("", response_model=MoodLogResponse)
async def create_mood_log(
    data: MoodLogCreate,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Save a feelings check-in (up to 3 emotions selected together)."""
    user_id = current_user.id if current_user else None
    
    # Enforce maximum 3 feelings
    tags = data.emotion_tags[:3] if data.emotion_tags else []
    tags_str = ",".join(tags)

    log = MoodLogModel(
        id=str(uuid.uuid4()),
        user_id=user_id,
        session_id=data.session_id,
        mood_score=data.mood_score,
        mood_label=data.mood_label,
        emotion_tags=tags_str,
        notes=data.notes
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)

    return MoodLogResponse(
        id=log.id,
        session_id=log.session_id,
        mood_score=log.mood_score,
        mood_label=log.mood_label,
        emotion_tags=log.emotion_tags.split(",") if log.emotion_tags else [],
        notes=log.notes,
        created_at=log.created_at
    )

@router.get("/history", response_model=List[MoodLogResponse])
async def list_mood_history(
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Fetch recorded feeling check-in logs for the user."""
    user_id = current_user.id if current_user else None
    stmt = select(MoodLogModel)
    if user_id:
        stmt = stmt.where(MoodLogModel.user_id == user_id)
    else:
        stmt = stmt.where(MoodLogModel.user_id == None)
        
    stmt = stmt.order_by(desc(MoodLogModel.created_at))
    result = await db.execute(stmt)
    logs = result.scalars().all()

    return [
        MoodLogResponse(
            id=l.id,
            session_id=l.session_id,
            mood_score=l.mood_score,
            mood_label=l.mood_label,
            emotion_tags=l.emotion_tags.split(",") if l.emotion_tags else [],
            notes=l.notes,
            created_at=l.created_at
        ) for l in logs
    ]

@router.get("/summary", response_model=MoodSummaryResponse)
async def get_mood_summary(
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Get summarized mood analytics and encouraging reflections."""
    user_id = current_user.id if current_user else None
    stmt = select(MoodLogModel)
    if user_id:
        stmt = stmt.where(MoodLogModel.user_id == user_id)
    else:
        stmt = stmt.where(MoodLogModel.user_id == None)
        
    stmt = stmt.order_by(desc(MoodLogModel.created_at)).limit(14)
    result = await db.execute(stmt)
    logs = result.scalars().all()

    if not logs:
        return MoodSummaryResponse(
            total_entries=0,
            average_score=0.0,
            recent_logs=[],
            dominant_emotions=[],
            encouragement_note="Taking a moment to check in with yourself is a wonderful habit. Log your first check-in whenever you feel ready!"
        )

    avg_score = sum(l.mood_score for l in logs) / len(logs)
    
    all_tags = []
    for l in logs:
        if l.emotion_tags:
            all_tags.extend([t.strip() for t in l.emotion_tags.split(",") if t.strip()])
    
    tag_counts = Counter(all_tags)
    dominant = [tag for tag, _ in tag_counts.most_common(3)]

    if avg_score >= 3.5:
        note = "You've been having some brighter moments recently. Acknowledge them and carry them with you."
    elif avg_score >= 2.5:
        note = "You are taking things one day at a time. Remember to be gentle with yourself through the ups and downs."
    else:
        note = "It looks like things have felt quite heavy lately. Please remember you don't have to carry it alone. Reach out to someone you trust."

    recent_responses = [
        MoodLogResponse(
            id=l.id,
            session_id=l.session_id,
            mood_score=l.mood_score,
            mood_label=l.mood_label,
            emotion_tags=l.emotion_tags.split(",") if l.emotion_tags else [],
            notes=l.notes,
            created_at=l.created_at
        ) for l in logs
    ]

    return MoodSummaryResponse(
        total_entries=len(logs),
        average_score=round(avg_score, 1),
        recent_logs=recent_responses,
        dominant_emotions=dominant,
        encouragement_note=note
    )
