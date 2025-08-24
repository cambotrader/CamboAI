from __future__ import annotations
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timedelta
import yfinance as yf

router = APIRouter(prefix="/api/v1/portfolio", tags=["Portfolio"]) 

# Demo positions (unauthenticated v1)
DEMO_POSITIONS = [
    {"symbol": "AAPL", "quantity": 10, "entry_price": 150.0, "entry_date": (datetime.utcnow() - timedelta(days=30)).isoformat()},
    {"symbol": "MSFT", "quantity": 5, "entry_price": 300.0, "entry_date": (datetime.utcnow() - timedelta(days=45)).isoformat()},
    {"symbol": "NVDA", "quantity": 3, "entry_price": 800.0, "entry_date": (datetime.utcnow() - timedelta(days=20)).isoformat()},
]


def _fetch_price(symbol: str) -> float:
    try:
        data = yf.Ticker(symbol).history(period="2d", interval="1d")
        if data is None or data.empty:
            raise ValueError("no data")
        return float(data["Close"].iloc[-1])
    except Exception:
        # Fallback hardcoded demo price
        return {
            "AAPL": 190.0,
            "MSFT": 410.0,
            "NVDA": 900.0,
        }.get(symbol, 100.0)


@router.get("/summary")
async def summary() -> Dict[str, Any]:
    try:
        rows: List[Dict[str, Any]] = []
        total_cost = 0.0
        total_value = 0.0
        for p in DEMO_POSITIONS:
            price = _fetch_price(p["symbol"])  # robust fallback inside
            mv = price * p["quantity"]
            cost = p["entry_price"] * p["quantity"]
            pnl = mv - cost
            total_cost += cost
            total_value += mv
            rows.append({
                **p,
                "current_price": round(price, 2),
                "market_value": round(mv, 2),
                "pnl": round(pnl, 2),
                "pnl_percentage": round((pnl / max(1e-9, cost)) * 100, 2),
            })
        total_pnl = total_value - total_cost
        ret_pct = (total_pnl / max(1e-9, total_cost)) * 100
        return {
            "positions": rows,
            "positions_count": len(rows),
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_pnl": round(total_pnl, 2),
            "total_return_percentage": round(ret_pct, 2),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))