from enum import Enum
from pydantic import BaseModel

class ConversationModeEnum(str, Enum):
    JUST_LISTEN = "just_listen"
    GIVE_ME_ADVICE = "give_me_advice"
    HELP_ME_UNDERSTAND = "help_me_understand"
    HELP_ME_TELL_SOMEONE = "help_me_tell_someone"

class ModeInfo(BaseModel):
    id: ConversationModeEnum
    title: str
    icon: str
    short_description: str
    prompt_guideline: str
