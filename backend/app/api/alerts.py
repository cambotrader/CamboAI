from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

router = APIRouter(prefix="/api/alerts", tags=["Alerts"]) 

# File-backed store (phase-1)
from app.services import alerts_service

class Rule(BaseModel):
    type: str = Field(..., description="price_cross | percent_move | time")
    symbol: Optional[str] = None
    op: Optional[str] = None  # >, <, >=, <=, ==
    threshold: Optional[float] = None
    window: Optional[str] = None  # e.g., 1h, 1d

class Alert(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    rule: Rule
    active: bool = True
    created_at: Optional[str] = None

@router.get("/rules")
async def list_rules():
    return {"items": alerts_service.list_rules()}

@router.post("/rules")
async def create_rule(alert: Alert):
    row = alerts_service.create_rule(alert.dict())
    return {"ok": True, "alert": row}

@router.post("/run")
async def run_once() -> Dict[str, Any]:
    return await alerts_service.evaluate_once()