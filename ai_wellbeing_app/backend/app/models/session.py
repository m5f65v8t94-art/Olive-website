import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), default="New Conversation")
    current_mode = Column(String(50), default="just_listen")  # just_listen, give_me_advice, help_me_understand, help_me_tell_someone
    context_summary = Column(Text, nullable=True)  # Rolling non-identifying context summary for continuity
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("UserModel", back_populates="sessions")
    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan", order_by="MessageModel.timestamp")
    mood_logs = relationship("MoodLogModel", back_populates="session", cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntryModel", back_populates="session", cascade="all, delete-orphan")
