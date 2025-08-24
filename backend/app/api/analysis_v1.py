from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import pandas as pd
import numpy as np
import yfinance as yf

router = APIRouter(prefix="/api/v1/analysis", tags=["Analysis"]) 

# Optional TA-Lib
try:
    import talib  # type: ignore
    HAS_TALIB = True
except Exception:
    talib = None  # type: ignore
    HAS_TALIB = False


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    if len(series) < period + 1:
        return pd.Series([np.nan] * len(series), index=series.index)
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean() + 1e-12
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def _bbands(series: pd.Series, period: int = 20, mult: float = 2.0):
    ma = series.rolling(window=period, min_periods=1).mean()
    sd = series.rolling(window=period, min_periods=1).std(ddof=0)
    upper = ma + mult * sd
    lower = ma - mult * sd
    return upper, ma, lower


@router.get("/technical")
async def technical(
    symbol: str = Query(..., description="Ticker symbol, e.g., AAPL"),
    period: str = Query("1mo", description="History period for yfinance"),
    interval: str = Query("1d", description="Interval for yfinance"),
) -> Dict[str, Any]:
    try:
        df = yf.Ticker(symbol).history(period=period, interval=interval)
        if df is None or df.empty:
            raise ValueError("No data returned")
        close = df["Close"].astype(float)

        if HAS_TALIB:
            sma = talib.SMA(close.values, timeperiod=20)
            rsi = talib.RSI(close.values, timeperiod=14)
            u, m, l = talib.BBANDS(close.values, timeperiod=20)
            out = {
                "sma": np.nan_to_num(sma).tolist(),
                "rsi": np.nan_to_num(rsi).tolist(),
                "bollinger_bands": {
                    "upper": np.nan_to_num(u).tolist(),
                    "middle": np.nan_to_num(m).tolist(),
                    "lower": np.nan_to_num(l).tolist(),
                },
            }
        else:
            sma = close.rolling(window=20, min_periods=1).mean()
            rsi = _rsi(close, period=14)
            u, m, l = _bbands(close, period=20)
            out = {
                "sma": sma.round(6).fillna(0.0).tolist(),
                "rsi": rsi.round(6).fillna(0.0).tolist(),
                "bollinger_bands": {
                    "upper": u.round(6).fillna(0.0).tolist(),
                    "middle": m.round(6).fillna(0.0).tolist(),
                    "lower": l.round(6).fillna(0.0).tolist(),
                },
            }
        return out
    except Exception as e:
        # Return minimal structure so UI doesn't break
        raise HTTPException(status_code=400, detail=str(e))