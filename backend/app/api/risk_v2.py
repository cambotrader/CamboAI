from __future__ import annotations
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel

from app.services.risk_v2 import get_risk_engine_v2
from app.core.metrics import MetricsManager
from app.core.auth import get_current_user_api_key
from app.models.trading_models import User as AuthUser
from app.services.user_preferences import get_user_preferences
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v2/risk", tags=["Risk v2"]) 

class RiskMetricsModel(BaseModel):
    volatility_annual: float
    max_drawdown: float
    var_95_daily: float
    es_95_daily: float
    sharpe: float

class RiskResponse(BaseModel):
    symbol: str
    version: str
    metrics: RiskMetricsModel
    detail: dict | None = None

@router.get("/summary", response_model=RiskResponse)
async def summary(
    symbol: str = Query("SPY"),
    period: str = Query("6mo"),
    interval: str = Query("1d"),
    preferred_provider: str | None = Query(None),
    current_user: AuthUser | None = Depends(get_current_user_api_key),
    db: Session = Depends(get_db)
):
    MetricsManager.record_analysis_request("risk_v2")
    if current_user and not preferred_provider:
        prefs = get_user_preferences(db, current_user)
        preferred_provider = prefs.preferred_market_data or preferred_provider
    out = get_risk_engine_v2().summarize(symbol=symbol, period=period, interval=interval, preferred_provider=preferred_provider)
    return out