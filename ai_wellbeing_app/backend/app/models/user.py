import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    pin_hash = Column(String(255), nullable=True)  # Salted hash for Protected History PIN
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    sessions = relationship("SessionModel", back_populates="user", cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntryModel", back_populates="user", cascade="all, delete-orphan")
    mood_logs = relationship("MoodLogModel", back_populates="user", cascade="all, delete-orphan")
