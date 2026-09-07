from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class JournalEntryCreate(BaseModel):
    session_id: Optional[str] = None
    title: Optional[str] = Field("My Thoughts Today", max_length=255)
    content: str = Field(..., min_length=1)
    prompt_used: Optional[str] = Field(None, max_length=255)
    emotion_tag: Optional[str] = Field(None, max_length=50)

class JournalEntryUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    emotion_tag: Optional[str] = Field(None, max_length=50)

class JournalEntryResponse(BaseModel):
    id: str
    session_id: Optional[str] = None
    title: str
    content: str
    prompt_used: Optional[str] = None
    emotion_tag: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class JournalPromptSuggestion(BaseModel):
    id: str
    category: str
    prompt_text: str
