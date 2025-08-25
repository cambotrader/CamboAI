from fastapi import APIRouter, Query, Header
from modules.options.provider import (
    get_chain, list_tradier_expirations,
    get_iv_rank, compute_greeks_black_scholes
)
from modules.options.analytics import iv_history, skew_snapshot, greeks_distribution
import pandas as pd

router = APIRouter(prefix="/options", tags=["options"])

@router.get("/chain")
def chain(symbol: str = Query("AAPL"), source: str = Query("tradier"), expiry: str | None = None):
    df = get_chain(symbol, source=source, expiry=expiry)
    return {"symbol":symbol,"rows":len(df),"chain":df.to_dict(orient="records")}

@router.get("/chain/with_greeks")
def chain_with_greeks(symbol: str = "AAPL", source: str = "tradier",
                      expiry: str | None = None, underlying: float = 100.0, dte: int = 30):
    df = get_chain(symbol, source=source, expiry=expiry)
    df = compute_greeks_black_scholes(df, underlying=underlying, dte=dte)
    return {"symbol":symbol,"rows":len(df),"chain":df.to_dict(orient="records")}

@router.get("/iv_rank")
def iv_rank(symbol: str, lookback: int = 180):
    rank = get_iv_rank(symbol, lookback_days=lookback)
    return {"symbol":symbol,"iv_rank":rank}

@router.get("/expirations")
def expirations(symbol: str, source: str = "tradier", token: str | None = Header(default=None)):
    if source != "tradier":
        return {"symbol":symbol,"expirations":[]}
    return {"symbol":symbol,"expirations": list_tradier_expirations(symbol, token or "")}

@router.get("/analytics")
def options_analytics(symbol: str = "AAPL", expiry: str | None = None):
    chain = get_chain(symbol, source="tradier", expiry=expiry)
    hist = iv_history(symbol)
    skew = skew_snapshot(chain)
    greeks = greeks_distribution(chain)
    return {
        "symbol": symbol,
        "rows": len(chain),
        "skew": skew,
        "iv_history_points": len(hist),
        "iv_history": hist.to_dict(orient="records"),
        "greeks_stats": greeks
    }