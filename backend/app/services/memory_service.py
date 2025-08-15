from __future__ import annotations
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.memory import UserMemory


def save_memory(db: Session, user_id: str, scope: str, key: str, value: str) -> UserMemory:
    m = UserMemory(user_id=user_id, scope=scope, key=key, value=value, updated_at=datetime.utcnow())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def get_recent_memories(db: Session, user_id: str, scope: str, limit: int = 5) -> List[UserMemory]:
    return (
        db.query(UserMemory)
        .filter_by(user_id=user_id, scope=scope)
        .order_by(UserMemory.created_at.desc())
        .limit(limit)
        .all()
    )

__all__ = ["save_memory", "get_recent_memories"]