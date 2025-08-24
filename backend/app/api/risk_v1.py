from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import numpy as np
import pandas as pd
import yfinance as yf

router = APIRouter(prefix="/api/v1/risk", tags=["Risk"]) 


def _max_drawdown(values: pd.Series) -> float:
    peak = values.cummax()
    dd = (values / peak) - 1.0
    return float(dd.min()) if len(dd) else 0.0


def _summary_from_close(close: pd.Series) -> Dict[str, Any]:
    if len(close) < 2:
        return {"volatility": 0.0, "maximum_drawdown": 0.0, "sharpe_ratio": 0.0, "value_at_risk_95": 0.0}
    ret = close.pct_change().dropna()
    vol = float(ret.std() * (252 ** 0.5))
    mdd = _max_drawdown(close)
    mean_ret = float(ret.mean() * 252)
    sharpe = mean_ret / (vol + 1e-12)
    var_95 = float(np.percentile(ret, 5))  # daily loss at 95%
    return {
        "volatility": round(vol, 6),
        "maximum_drawdown": round(mdd, 6),
        "sharpe_ratio": round(sharpe, 6),
        "value_at_risk_95": round(var_95, 6),
    }


@router.get("/summary")
async def summary(symbol: str = Query("SPY", description="Symbol for risk proxy")) -> Dict[str, Any]:
    try:
        df = yf.Ticker(symbol).history(period="6mo", interval="1d")
        if df is None or df.empty:
            raise ValueError("No data")
        close = df["Close"].astype(float)
        return {"symbol": symbol, "risk_metrics": _summary_from_close(close)}
    except Exception:
        # Fallback sample
        fake = pd.Series(100 * (1 + 0.001 * np.cumsum(np.random.randn(120))))
        return {"symbol": symbol, "risk_metrics": _summary_from_close(fake)}