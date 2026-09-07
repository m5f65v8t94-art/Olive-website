from app.config import settings
from app.services.ai_service import AIProvider
from app.services.local_engine import local_engine, LocalEmpatheticEngine
from app.services.ollama_service import ollama_provider, OllamaProvider
from app.services.safety_service import safety_service, SafetyService
from app.services.continuity_service import continuity_service, ContinuityService

def get_ai_provider() -> AIProvider:
    """Returns the configured AI provider engine."""
    if settings.AI_PROVIDER == "ollama":
        return ollama_provider
    return local_engine

__all__ = [
    "AIProvider",
    "LocalEmpatheticEngine",
    "local_engine",
    "OllamaProvider",
    "ollama_provider",
    "SafetyService",
    "safety_service",
    "ContinuityService",
    "continuity_service",
    "get_ai_provider"
]
