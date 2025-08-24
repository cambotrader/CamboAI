from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any

from app.services.signals import generate_signal

router = APIRouter(prefix="/api/v1", tags=["Signals"]) 

@router.get("/signals")
async def get_signal(
    symbol: Optional[str] = Query(default=None, description="Ticker symbol, e.g., AAPL"),
    timeframe: str = Query(default="1D", regex="^(1D|1d|1h|1H|1wk|1W)$"),
    period: str = Query(default="6mo", description="History window for yfinance"),
) -> Dict[str, Any]:
    try:
        return generate_signal(symbol, timeframe=timeframe, period=period)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))