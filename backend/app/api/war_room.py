from __future__ import annotations
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Literal, Dict
from datetime import datetime

from app.database import get_db
from app.services.pii_moderator import sanitize
from app.models.social import DebateLog, DebateReply
from app.services.llm_provider import generate_text

router = APIRouter(prefix="/api/war-room", tags=["AI War Room"])

class DebateAgent(BaseModel):
    name: str
    role: Literal["strategist", "risk", "sentiment", "macro", "technicals", "options"]

class DebateRequest(BaseModel):
    user_id: str
    user_prompt: str
    agents: List[DebateAgent] = [
        DebateAgent(name="Strategist", role="strategist"),
        DebateAgent(name="Risk", role="risk"),
        DebateAgent(name="Sentiment", role="sentiment"),
        DebateAgent(name="Macro", role="macro"),
        DebateAgent(name="Technicals", role="technicals"),
        DebateAgent(name="Options", role="options"),
    ]

class AgentReply(BaseModel):
    agent: str
    role: str
    view: str
    confidence: float

class DebateResponse(BaseModel):
    sanitized_prompt: str
    redactions: Dict[str, bool]
    replies: List[AgentReply]
    consensus: str
    debate_id: str
    timestamp: str

@router.post("/debate", response_model=DebateResponse)
async def run_debate(payload: DebateRequest, db=Depends(get_db)):
    prompt, flags = sanitize(payload.user_prompt)

    # LLM-backed multi-agent debate (free-first via provider abstraction)
    replies: List[AgentReply] = []
    for a in payload.agents:
        system = f"You are the {a.role} advisor in a trading council. Provide concise, high-signal insights."
        user_msg = [{"role": "user", "content": f"User prompt: {prompt}"}]
        view = generate_text(system, user_msg)
        # Heuristic confidence (can improve later):
        conf = 0.75 if a.role in ("sentiment", "macro") else 0.82
        replies.append(AgentReply(agent=a.name, role=a.role, view=view, confidence=conf))

    # Voting/consensus: highest confidence wins for now
    top = max(replies, key=lambda r: r.confidence)
    consensus = f"Consensus: {top.view}"

    # Persist debate and replies
    try:
        log = DebateLog(user_id=payload.user_id, prompt=prompt, consensus=consensus)
        db.add(log)
        db.flush()  # to get log.id
        for r in replies:
            db.add(DebateReply(
                debate_id=log.id,
                agent=r.agent,
                role=r.role,
                view=r.view,
                confidence=str(r.confidence),
            ))
        db.commit()
        debate_id = log.id
    except Exception:
        db.rollback()
        debate_id = "debate-" + datetime.utcnow().strftime("%Y%m%d%H%M%S")

    return DebateResponse(
        sanitized_prompt=prompt,
        redactions=flags,
        replies=replies,
        consensus=consensus,
        debate_id=debate_id,
        timestamp=datetime.utcnow().isoformat(),
    )