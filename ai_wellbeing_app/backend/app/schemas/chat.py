from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.mode import ConversationModeEnum
from app.schemas.safety import SafetyAssessment

class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    mode: Optional[ConversationModeEnum] = None

class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    mode: Optional[str] = None
    is_safety_flagged: bool = False
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatSessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    initial_mode: Optional[ConversationModeEnum] = ConversationModeEnum.JUST_LISTEN

class ChatSessionUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)

class ChatSessionResponse(BaseModel):
    id: str
    title: str
    current_mode: str
    context_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    latest_message_preview: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ChatTurnRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1)
    mode: ConversationModeEnum = ConversationModeEnum.JUST_LISTEN

class ChatTurnResponse(BaseModel):
    session_id: str
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
    current_mode: ConversationModeEnum
    safety_assessment: SafetyAssessment
