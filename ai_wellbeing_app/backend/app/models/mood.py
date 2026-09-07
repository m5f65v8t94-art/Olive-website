import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class MoodLogModel(Base):
    __tablename__ = "mood_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    mood_score = Column(Integer, nullable=False)  # 1 (lowest) to 5 (highest)
    mood_label = Column(String(50), nullable=False)  # e.g., "Overwhelmed", "Anxious", "Neutral", "Hopeful", "Calm"
    emotion_tags = Column(String(255), nullable=True)  # Comma-separated tags (up to 3): "tired,lonely,stressed"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("UserModel", back_populates="mood_logs")
    session = relationship("SessionModel", back_populates="mood_logs")
