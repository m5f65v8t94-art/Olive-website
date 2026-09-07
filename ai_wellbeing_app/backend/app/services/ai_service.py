from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class AIProvider(ABC):
    """Abstract base class for all AI providers."""

    @abstractmethod
    async def generate_response(
        self,
        mode: str,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context_summary: Optional[str] = None
    ) -> str:
        """Generate a response according to the requested conversation mode."""
        pass

    @abstractmethod
    async def generate_tell_someone_draft(
        self,
        recipient: str,
        tone: str,
        core_feeling: str,
        what_i_need: Optional[str] = None,
        preferred_medium: Optional[str] = "text"
    ) -> Dict[str, Any]:
        """Generate a structured message draft for reaching out to someone."""
        pass
