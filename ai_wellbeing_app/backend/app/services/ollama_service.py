import json
import httpx
from typing import List, Dict, Any, Optional
from app.config import settings
from app.services.ai_service import AIProvider
from app.services.local_engine import local_engine
from app.utils.constants import CONVERSATION_MODES, NON_CLINICAL_DISCLAIMER

class OllamaProvider(AIProvider):
    """
    Adapter for Local LLMs running via Ollama (e.g. Llama 3.2, Mistral, Gemma).
    If Ollama is not running or unreachable, gracefully falls back to the LocalEmpatheticEngine.
    """

    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL, model: str = settings.OLLAMA_MODEL):
        self.base_url = base_url
        self.model = model

    async def generate_response(
        self,
        mode: str,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context_summary: Optional[str] = None
    ) -> str:
        mode_info = CONVERSATION_MODES.get(mode, CONVERSATION_MODES["just_listen"])
        guideline = mode_info["prompt_guideline"]

        system_prompt = (
            f"You are Liv, a warm, emotionally intelligent, slightly sassy and understanding 'cool older sister' AI companion for Olive (Youth Mental Wellbeing Support). "
            f"{NON_CLINICAL_DISCLAIMER}\n\n"
            f"CORE BEHAVIOR:\n"
            f"1. Listen first and notice specific details the user described (e.g. specific conditions like vitiligo, exam deadlines, feeling left out, stares, dismissive comments).\n"
            f"2. Validate their exact emotional reality in an authentic, conversational voice. Never give generic boilerplate responses that could apply to anyone.\n"
            f"3. DO NOT output bullet points, numbered lists, self-help worksheets, meditation or breathing exercises unless in 'Give Me Advice' mode or specifically asked.\n"
            f"4. Unless in 'Give Me Advice' mode, DO NOT jump to solutions or unsolicited advice. Focus on genuine listening and solidarity.\n"
            f"5. End with ONE thoughtful, open-ended follow-up question related specifically to what the user said.\n"
            f"6. Never diagnose, label, or sound like a clinical doctor or therapist.\n\n"
            f"MODE GUIDELINE:\n{guideline}\n"
        )
        if context_summary:
            system_prompt += f"\nPrevious Context Summary for continuity:\n{context_summary}\n"

        messages = [{"role": "system", "content": system_prompt}]
        for hist in conversation_history[-settings.MAX_HISTORY_MESSAGES_CONTEXT:]:
            messages.append({"role": hist["role"], "content": hist["content"]})
        messages.append({"role": "user", "content": user_message})

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": 0.7}
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("message", {}).get("content", "")
        except Exception:
            # Fallback seamlessly to local engine
            pass

        return await local_engine.generate_response(mode, user_message, conversation_history, context_summary)

    async def generate_tell_someone_draft(
        self,
        recipient: str,
        tone: str,
        core_feeling: str,
        what_i_need: Optional[str] = None,
        preferred_medium: Optional[str] = "text"
    ) -> Dict[str, Any]:
        return await local_engine.generate_tell_someone_draft(recipient, tone, core_feeling, what_i_need, preferred_medium)

ollama_provider = OllamaProvider()
