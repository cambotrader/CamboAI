from __future__ import annotations
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd

router = APIRouter(prefix="/api/v1/md", tags=["Market Data Extra"]) 

class OHLCV(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class SeriesResponse(BaseModel):
    symbol: str
    provider: str
    data: List[OHLCV]

# Minimal, safe synthetic fallbacks for crypto, FX, options (stub)

def _synthetic_series(days: int = 30) -> pd.DataFrame:
    idx = pd.date_range(end=pd.Timestamp.utcnow().normalize(), periods=days, freq="D")
    base = 100 * (1 + 0.001 * pd.Series(range(days))).astype(float)
    df = pd.DataFrame({
        "Open": base,
        "High": base * 1.002,
        "Low": base * 0.998,
        "Close": base * 1.0005,
        "Volume": 1_000_000,
    }, index=idx)
    return df

from app.services.md_crypto import get_crypto_provider

@router.get("/crypto/ohlcv", response_model=SeriesResponse)
async def crypto_ohlcv(symbol: str = Query("BTC-USD"), days: int = Query(30)):
    # Try real provider, fallback to synthetic
    out = get_crypto_provider().fetch_ohlcv(symbol, days)
    df = out["df"] if isinstance(out, dict) else None
    provider = out.get("provider") if isinstance(out, dict) else "synthetic"
    if df is None or df.empty:
        df = _synthetic_series(days)
        provider = provider or "synthetic"
    # sanitize and coerce to finite floats
    df = df.fillna(method="ffill").fillna(method="bfill").fillna(0)
    def _finite(x: float) -> float:
        try:
            xv = float(x)
            if xv != xv or xv in (float("inf"), float("-inf")):
                return 0.0
            return xv
        except Exception:
            return 0.0
    return SeriesResponse(
        symbol=symbol,
        provider=provider,
        data=[OHLCV(date=str(i.date()), open=_finite(r.Open), high=_finite(r.High), low=_finite(r.Low), close=_finite(r.Close), volume=_finite(r.Volume)) for i, r in df.iterrows()],
    )

from app.services.md_fx import get_fx_provider

@router.get("/fx/ohlcv", response_model=SeriesResponse)
async def fx_ohlcv(symbol: str = Query("EURUSD"), days: int = Query(30)):
    out = get_fx_provider().fetch_ohlcv(symbol, days)
    df = out["df"] if isinstance(out, dict) else None
    provider = out.get("provider") if isinstance(out, dict) else "synthetic"
    if df is None or df.empty:
        df = _synthetic_series(days)
        provider = provider or "synthetic"
    # sanitize and coerce to finite floats
    df = df.fillna(method="ffill").fillna(method="bfill").fillna(0)
    def _finite(x: float) -> float:
        try:
            xv = float(x)
            if xv != xv or xv in (float("inf"), float("-inf")):
                return 0.0
            return xv
        except Exception:
            return 0.0
    return SeriesResponse(
        symbol=symbol,
        provider=provider,
        data=[OHLCV(date=str(i.date()), open=_finite(r.Open), high=_finite(r.High), low=_finite(r.Low), close=_finite(r.Close), volume=_finite(r.Volume)) for i, r in df.iterrows()],
    )

from app.services.md_options import get_options_provider

@router.get("/options/ohlcv", response_model=SeriesResponse)
async def options_ohlcv(symbol: str = Query("AAPL230915C00175000"), days: int = Query(30)):
    out = get_options_provider().fetch_ohlcv(symbol, days)
    df = out["df"] if isinstance(out, dict) else None
    provider = out.get("provider") if isinstance(out, dict) else "synthetic"
    if df is None or df.empty:
        df = _synthetic_series(days)
        provider = provider or "synthetic"
    # sanitize and coerce to finite floats
    df = df.fillna(method="ffill").fillna(method="bfill").fillna(0)
    def _finite(x: float) -> float:
        try:
            xv = float(x)
            if xv != xv or xv in (float("inf"), float("-inf")):
                return 0.0
            return xv
        except Exception:
            return 0.0
    return SeriesResponse(
        symbol=symbol,
        provider=provider,
        data=[OHLCV(date=str(i.date()), open=_finite(r.Open), high=_finite(r.High), low=_finite(r.Low), close=_finite(r.Close), volume=_finite(r.Volume)) for i, r in df.iterrows()],
    )