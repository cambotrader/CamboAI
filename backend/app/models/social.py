from __future__ import annotations
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id = Column(String, ForeignKey("chat_rooms.id"), index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    text = Column(Text, nullable=False)
    redacted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DirectMessage(Base):
    __tablename__ = "direct_messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    to_user_id = Column(String, index=True, nullable=False)
    from_user_id = Column(String, index=True, nullable=False)
    text = Column(Text, nullable=False)
    redacted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DebateLog(Base):
    __tablename__ = "debate_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    prompt = Column(Text, nullable=False)
    consensus = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DebateReply(Base):
    __tablename__ = "debate_replies"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    debate_id = Column(String, ForeignKey("debate_logs.id"), index=True, nullable=False)
    agent = Column(String, nullable=False)
    role = Column(String, nullable=False)
    view = Column(Text, nullable=False)
    confidence = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)