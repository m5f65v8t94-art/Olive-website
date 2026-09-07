from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class RecipientType(str, Enum):
    PARENT_GUARDIAN = "parent_guardian"
    SCHOOL_COUNSELOR = "school_counselor"
    TEACHER = "teacher"
    FRIEND = "friend"
    SIBLING = "sibling"
    TRUSTED_ADULT = "trusted_adult"

class MessageTone(str, Enum):
    CASUAL_TEXT = "casual_text"
    DIRECT_HONEST = "direct_honest"
    GENTLE_VULNERABLE = "gentle_vulnerable"
    FORMAL_LETTER = "formal_letter"
    IN_PERSON_STARTER = "in_person_starter"

class TellSomeoneRequest(BaseModel):
    recipient: RecipientType
    tone: MessageTone
    core_feeling: str = Field(..., min_length=2, description="What the user wants to communicate (e.g. feeling overwhelmed with exams)")
    what_i_need: Optional[str] = Field(None, description="What kind of response they want, e.g., just someone to listen, help getting support, or space")
    preferred_medium: Optional[str] = Field("text", description="text, in_person, email, note")

class DraftVariation(BaseModel):
    title: str
    content: str
    recommended_medium: str
    tips: List[str]

class TellSomeoneResponse(BaseModel):
    recipient: RecipientType
    tone: MessageTone
    primary_draft: str
    alternative_drafts: List[DraftVariation]
    conversation_tips: List[str]
    encouragement: str
