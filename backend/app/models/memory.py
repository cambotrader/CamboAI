from __future__ import annotations
from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime
import uuid

from app.database import Base

class UserMemory(Base):
    __tablename__ = "user_memories"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    scope = Column(String, default="general")  # coach|therapy|warroom|community
    key = Column(String, index=True, nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)