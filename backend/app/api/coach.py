from __future__ import annotations
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Literal, Dict, List
from datetime import datetime

from app.database import get_db
from app.services.pii_moderator import sanitize
from app.services.llm_provider import generate_text

router = APIRouter(prefix="/api/coach", tags=["AI Coach & Therapy"])

class MarketContext(BaseModel):
    ticker: str
    price: Optional[float] = None
    rsi: Optional[float] = None
    atr: Optional[float] = None
    trend: Optional[Literal["up", "down", "sideways"]] = None
    sentiment: Optional[Literal["bullish", "bearish", "neutral"]] = None

class TradeState(BaseModel):
    position: Optional[Literal["flat", "long", "short"]] = "flat"
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    risk_per_trade_pct: Optional[float] = 1.0

class CoachRequest(BaseModel):
    user_id: str
    user_message: str
    mode: Literal["coach", "therapy"] = "coach"
    market: Optional[MarketContext] = None
    trade: Optional[TradeState] = None

class CoachResponse(BaseModel):
    reply: str
    redactions: Dict[str, bool]
    alerts: List[str] = []
    timestamp: str


def rule_advice(market: MarketContext | None, trade: TradeState | None) -> List[str]:
    alerts: List[str] = []
    if not market or not trade:
        return alerts
    if trade.position != "flat" and trade.stop_loss is None:
        alerts.append("Warning: No stop loss set. Consider defining a protective stop.")
    if trade.position != "flat" and trade.take_profit is None:
        alerts.append("Reminder: No take-profit target set. Define targets to lock gains.")
    if market.rsi is not None:
        if market.rsi > 70:
            alerts.append("RSI > 70 suggests overbought conditions. Be cautious with new longs.")
        if market.rsi < 30:
            alerts.append("RSI < 30 suggests oversold conditions. Watch for reversal strength.")
    if market.sentiment == "bearish" and trade.position == "long":
        alerts.append("Bearish sentiment while long. Tighten stops or reduce size if conviction is low.")
    if market.sentiment == "bullish" and trade.position == "short":
        alerts.append("Bullish sentiment while short. Ensure risk is controlled.")
    if market.atr and trade.entry_price and trade.position != "flat" and trade.stop_loss is None:
        sl = trade.entry_price - 1.5 * market.atr if trade.position == "long" else trade.entry_price + 1.5 * market.atr
        alerts.append(f"Suggested stop-loss based on ATR: {sl:.2f}")
    return alerts

@router.post("/message", response_model=CoachResponse)
async def coach_message(payload: CoachRequest, db=Depends(get_db)):
    # Sanitize for PII
    clean, flags = sanitize(payload.user_message)

    # Placeholder LLM selection: use a free route later; for now, rule-based + echo
    system = "You are an expert trading coach and therapist. Be supportive and practical. Respect risk management."
    if payload.mode == "therapy":
        messages = [
            {"role": "user", "content": f"Therapy request: {clean}"}
        ]
        reply = generate_text(system, messages)
        return CoachResponse(reply=reply, redactions=flags, alerts=[], timestamp=datetime.utcnow().isoformat())
    else:
        alerts = rule_advice(payload.market, payload.trade)
        ctx = f"Market={payload.market.dict() if payload.market else {}}, Trade={payload.trade.dict() if payload.trade else {}}"
        messages = [
            {"role": "user", "content": f"Coach request: {clean}\nContext: {ctx}"}
        ]
        reply = generate_text(system, messages)
        return CoachResponse(reply=reply, redactions=flags, alerts=alerts, timestamp=datetime.utcnow().isoformat())