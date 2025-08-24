from __future__ import annotations
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.core.metrics import MetricsManager
from app.services.signals_v2 import get_signals_model_v2
# Soft auth dependency resolution (prefer API key auth when available)
try:
    from app.core.auth import get_current_user_api_key as get_current_user_api_key
except Exception:
    try:
        from app.api.auth import get_current_user as get_current_user_api_key
    except Exception:
        def get_current_user_api_key():
            return None

from app.models.trading_models import User as AuthUser
from app.services.user_preferences import get_user_preferences
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v2", tags=["Signals v2"])

class SignalDetail(BaseModel):
    symbol: str
    features: Dict[str, float]
    provider: str
    period: str
    interval: str

class SignalResponse(BaseModel):
    label: str = Field(pattern="^(BUY|SELL|NEUTRAL)$")
    score: float
    confidence: float
    version: str
    detail: SignalDetail | Dict[str, Any]

@router.get("/signals", response_model=SignalResponse)
async def signals(
    symbol: str = Query(..., description="Ticker symbol"),
    period: str = Query("3mo"),
    interval: str = Query("1d"),
    preferred_provider: str | None = Query(None, description="Override preferred market data provider"),
    current_user: Optional[AuthUser] = Depends(get_current_user_api_key),
    db: Session = Depends(get_db)
):
    MetricsManager.record_analysis_request("signals_v2")
    # Public GET allowed; if API-key user available, use their preference
    if current_user and not preferred_provider:
        prefs = get_user_preferences(db, current_user)
        preferred_provider = prefs.preferred_market_data or preferred_provider
    model = get_signals_model_v2()
    out = model.predict(symbol=symbol, period=period, interval=interval, preferred_provider=preferred_provider)
    return SignalResponse(
        label=out.label,
        score=out.score,
        confidence=out.confidence,
        version=out.version,
        detail=out.detail,
    )