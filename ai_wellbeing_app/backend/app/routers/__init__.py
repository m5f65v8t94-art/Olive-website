from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.tell_someone import router as tell_someone_router
from app.routers.mood import router as mood_router
from app.routers.journal import router as journal_router
from app.routers.resources import router as resources_router
from app.routers.history import router as history_router

__all__ = [
    "auth_router",
    "chat_router",
    "tell_someone_router",
    "mood_router",
    "journal_router",
    "resources_router",
    "history_router"
]
