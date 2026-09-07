from fastapi import APIRouter
from app.schemas.tell_someone import TellSomeoneRequest, TellSomeoneResponse, DraftVariation
from app.services import get_ai_provider

router = APIRouter(prefix="/api/help-me-tell-someone", tags=["Help Me Tell Someone"])

@router.post("", response_model=TellSomeoneResponse)
async def generate_tell_someone_draft(request: TellSomeoneRequest):
    """
    Generates tailored message drafts and conversation starters
    for a chosen recipient (parent, friend, teacher, counselor, etc.) and tone.
    """
    provider = get_ai_provider()
    result = await provider.generate_tell_someone_draft(
        recipient=request.recipient.value,
        tone=request.tone.value,
        core_feeling=request.core_feeling,
        what_i_need=request.what_i_need,
        preferred_medium=request.preferred_medium
    )

    return TellSomeoneResponse(
        recipient=request.recipient,
        tone=request.tone,
        primary_draft=result["primary_draft"],
        alternative_drafts=[DraftVariation(**v) for v in result["alternative_drafts"]],
        conversation_tips=result["conversation_tips"],
        encouragement=result["encouragement"]
    )
