from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.progress_service import log_progress, read_logs

router = APIRouter(prefix="/api", tags=["Modules","Progress"])

# 1) Pattern Scanner stubs
class ScanRequest(BaseModel):
    symbol: str
    timeframe: str = "1D"
    indicators: Optional[Dict[str, Any]] = None

from app.services import patterns as patterns_service

@router.post("/patterns/scan")
async def scan_patterns(body: ScanRequest):
    log_progress("patterns", "scan", details=f"{body.symbol} {body.timeframe}")
    try:
        return patterns_service.scan(symbol=body.symbol, timeframe=body.timeframe)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 2) Strategy Engine stubs
class StrategyRegister(BaseModel):
    name: str
    rules: List[Dict[str, Any]]  # [{type, field, op, value}]

@router.post("/strategy/register")
async def register_strategy(body: StrategyRegister):
    log_progress("strategy", "register", details=body.name)
    return {"ok": True, "strategy_id": f"strat-{int(datetime.utcnow().timestamp())}"}

class StrategyRun(BaseModel):
    strategy_id: str
    symbol: str
    timeframe: str = "1D"

@router.post("/strategy/run")
async def run_strategy(body: StrategyRun):
    log_progress("strategy", "run", details=f"{body.strategy_id} {body.symbol}")
    return {
        "strategy_id": body.strategy_id,
        "symbol": body.symbol,
        "metrics": {"win_rate": 0.58, "sharpe": 1.1, "max_drawdown": -0.12},
        "trades": [
            {"t": "2024-06-01", "side": "buy", "price": 100.0},
            {"t": "2024-06-15", "side": "sell", "price": 112.0},
        ],
    }

# 3) News & Sentiment stubs
from app.services import news_sentiment as ns_service

@router.get("/news/headlines")
async def get_headlines(symbol: Optional[str] = None, sources: Optional[str] = None, limit: int = 25):
    """sources: comma-separated list, e.g. "yahoo,google,reddit"""
    log_progress("news", "headlines", details=f"{symbol or 'all'} [{sources or 'default'}]")
    try:
        src_list = [s.strip() for s in sources.split(',')] if sources else None
        return ns_service.headlines(symbol, sources=src_list, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sentiment/summary")
async def get_sentiment(symbol: Optional[str] = None, sources: Optional[str] = None, limit: int = 50):
    log_progress("sentiment", "summary", details=f"{symbol or 'all'} [{sources or 'default'}]")
    try:
        src_list = [s.strip() for s in sources.split(',')] if sources else None
        return ns_service.sentiment_summary(symbol, sources=src_list, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 4) Options payoff stub
class PayoffRequest(BaseModel):
    strategy: str  # e.g. covered_call, iron_condor
    underlying_price: float
    params: Dict[str, Any]

@router.post("/options/payoff")
async def options_payoff(body: PayoffRequest):
    log_progress("options", "payoff", details=body.strategy)
    # Return demo payoff points
    prices = [body.underlying_price * (1 + x/100) for x in range(-20, 21, 5)]
    pnl = [round((p - body.underlying_price) * 0.6, 2) for p in prices]
    return {"prices": prices, "pnl": pnl}

# 5) Journal stubs
class JournalEntry(BaseModel):
    symbol: str
    notes: str
    tags: Optional[List[str]] = None

_JOURNAL_MEM: List[Dict[str, Any]] = []

@router.get("/journal/entries")
async def list_entries():
    return {"items": _JOURNAL_MEM[-100:]}

@router.post("/journal/entries")
async def create_entry(e: JournalEntry):
    item = {"id": len(_JOURNAL_MEM) + 1, "t": datetime.utcnow().isoformat(), **e.dict()}
    _JOURNAL_MEM.append(item)
    log_progress("journal", "create", details=e.symbol)
    return {"ok": True, "entry": item}

# 6) Alerts stubs
_ALERT_RULES: List[Dict[str, Any]] = []

@router.get("/alerts/rules")
async def list_alert_rules():
    return {"items": _ALERT_RULES}

@router.post("/alerts/rules")
async def create_alert_rule(rule: Dict[str, Any]):
    rule = {"id": len(_ALERT_RULES) + 1, **rule}
    _ALERT_RULES.append(rule)
    log_progress("alerts", "create", details=str(rule.get('id')))
    return {"ok": True, "rule": rule}

@router.post("/alerts/run")
async def run_alerts():
    log_progress("alerts", "run")
    # Return no alerts or sample
    return {"alerts": []}

# 7) Universal scanner stub
class ScannerRequest(BaseModel):
    universe: str = "stocks"  # stocks|crypto|fx|bonds
    filters: Optional[Dict[str, Any]] = None

@router.post("/scanner/run")
async def run_scanner(body: ScannerRequest):
    log_progress("scanner", "run", details=body.universe)
    return {"rows": [
        {"symbol": "AAPL", "score": 0.81, "pattern": "Triangle", "sentiment": "🟢"},
        {"symbol": "TSLA", "score": 0.64, "pattern": "Cup & Handle", "sentiment": "⚪"},
    ]}

# 8) War Room / Debate stubs
class DebateStart(BaseModel):
    topic: str
    agents: Optional[List[str]] = None

_DEBATES: Dict[str, Dict[str, Any]] = {}

@router.post("/war-room/debate/start")
async def start_debate(body: DebateStart):
    did = f"deb-{int(datetime.utcnow().timestamp())}"
    _DEBATES[did] = {
        "id": did,
        "topic": body.topic,
        "agents": body.agents or ["Quant", "Macro", "TA"],
        "consensus": "Neutral bias with breakout potential.",
        "replies": [
            {"agent": "Quant", "text": "Momentum positive; z-score 1.2"},
            {"agent": "Macro", "text": "CPI benign; liquidity stable"},
        ],
        "created_at": datetime.utcnow().isoformat()
    }
    log_progress("war-room", "start", details=did)
    return _DEBATES[did]

@router.get("/war-room/debate/{debate_id}")
async def get_debate(debate_id: str):
    row = _DEBATES.get(debate_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return row

# 9) Progress log feed for UI polling
@router.get("/progress/logs")
async def get_progress_logs(limit: int = 200):
    return {"items": read_logs(limit=limit)}

# 10) Pattern catalog for UI hover tooltips
@router.get("/patterns/catalog")
async def get_pattern_catalog():
    try:
        from app.services import pattern_catalog as pc
        return pc.catalog()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 11) Keys management (user-supplied API keys)
class KeyUpsert(BaseModel):
    values: Dict[str, Any]

@router.get("/keys/status")
async def get_keys_status():
    try:
        from app.services import keys as keys_service
        return {"status": keys_service.status()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/keys")
async def get_keys():
    try:
        from app.services import keys as keys_service
        return keys_service.get_all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/keys/{provider}")
async def set_keys(provider: str, body: KeyUpsert):
    try:
        from app.services import keys as keys_service
        updated = keys_service.set_key(provider, body.values)
        return {"provider": provider, "ok": True, "values": {k: ("***" if v else None) for k, v in updated.items()}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))