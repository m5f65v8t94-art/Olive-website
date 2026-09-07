from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class MoodLogCreate(BaseModel):
    session_id: Optional[str] = None
    mood_score: int = Field(..., ge=1, le=5, description="1 (Very Down) to 5 (Great)")
    mood_label: str = Field(..., max_length=50)
    emotion_tags: Optional[List[str]] = Field(default=[], description="List of emotion tags, e.g., ['Anxious', 'Tired']")
    notes: Optional[str] = Field(None, max_length=1000)

class MoodLogResponse(BaseModel):
    id: str
    session_id: Optional[str] = None
    mood_score: int
    mood_label: str
    emotion_tags: List[str]
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MoodSummaryResponse(BaseModel):
    total_entries: int
    average_score: float
    recent_logs: List[MoodLogResponse]
    dominant_emotions: List[str]
    encouragement_note: str
