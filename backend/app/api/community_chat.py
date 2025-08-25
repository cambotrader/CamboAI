from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Literal
from datetime import datetime

from sqlalchemy.orm import Session
from app.database import get_db
from app.services.pii_moderator import sanitize
from app.models.social import ChatRoom as ChatRoomModel, ChatMessage as ChatMessageModel, DirectMessage as DirectMessageModel

router = APIRouter(prefix="/api/community", tags=["Community Chat"])

Room = Literal["stocks", "options", "forex", "futures", "crypto", "lounge", "debate"]

DEFAULT_ROOMS = [
    {"slug": "stocks", "title": "Stocks"},
    {"slug": "options", "title": "Options"},
    {"slug": "forex", "title": "Forex"},
    {"slug": "futures", "title": "Futures"},
    {"slug": "crypto", "title": "Crypto"},
    {"slug": "lounge", "title": "Anything / Lounge"},
    {"slug": "debate", "title": "Debate Room"},
]

class ChatMessage(BaseModel):
    room: Room
    user_id: str
    text: str

class PostResponse(BaseModel):
    ok: bool
    redactions: Dict[str, bool]

class MessageDTO(BaseModel):
    room: Room
    user_id: str
    text: str
    timestamp: str

@router.post("/init")
async def init_rooms(db: Session = Depends(get_db)):
    for r in DEFAULT_ROOMS:
        exists = db.query(ChatRoomModel).filter_by(slug=r["slug"]).first()
        if not exists:
            db.add(ChatRoomModel(slug=r["slug"], title=r["title"]))
    db.commit()
    return {"ok": True}

@router.get("/rooms")
async def list_rooms(db: Session = Depends(get_db)):
    rows = db.query(ChatRoomModel).all()
    return {"rooms": [{"slug": r.slug, "title": r.title} for r in rows]}

@router.get("/history/{room}", response_model=List[MessageDTO])
async def room_history(room: Room, db: Session = Depends(get_db)):
    room_row = db.query(ChatRoomModel).filter_by(slug=room).first()
    if not room_row:
        raise HTTPException(status_code=404, detail="Room not found")
    msgs = (
        db.query(ChatMessageModel)
        .filter_by(room_id=room_row.id)
        .order_by(ChatMessageModel.created_at.desc())
        .limit(200)
        .all()
    )
    msgs.reverse()
    return [MessageDTO(room=room, user_id=m.user_id, text=m.text, timestamp=m.created_at.isoformat()) for m in msgs]

@router.post("/post", response_model=PostResponse)
async def post_message(payload: ChatMessage, db: Session = Depends(get_db)):
    clean, flags = sanitize(payload.text)
    room_row = db.query(ChatRoomModel).filter_by(slug=payload.room).first()
    if not room_row:
        raise HTTPException(status_code=404, detail="Room not found")
    db.add(ChatMessageModel(room_id=room_row.id, user_id=payload.user_id, text=clean, redacted=any(flags.values())))
    db.commit()
    return PostResponse(ok=True, redactions=flags)

class DirectMessage(BaseModel):
    to_user_id: str
    from_user_id: str
    text: str

@router.post("/dm", response_model=PostResponse)
async def send_dm(payload: DirectMessage, db: Session = Depends(get_db)):
    clean, flags = sanitize(payload.text)
    db.add(DirectMessageModel(to_user_id=payload.to_user_id, from_user_id=payload.from_user_id, text=clean, redacted=any(flags.values())))
    db.commit()
    return PostResponse(ok=True, redactions=flags)

@router.get("/dm/{user_id}")
async def list_dm(user_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(DirectMessageModel)
        .filter_by(to_user_id=user_id)
        .order_by(DirectMessageModel.created_at.desc())
        .limit(200)
        .all()
    )
    rows.reverse()
    return [{"from": r.from_user_id, "text": r.text, "timestamp": r.created_at.isoformat()} for r in rows]