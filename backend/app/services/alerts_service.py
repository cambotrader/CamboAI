from __future__ import annotations
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import json
import math
import yfinance as yf

_STORE = Path(__file__).resolve().parents[2] / "logs" / "alerts_store.json"
_STORE.parent.mkdir(parents=True, exist_ok=True)

# -------- Persistence --------

def _load_store() -> Dict[str, Any]:
    if not _STORE.exists():
        return {"rules": []}
    try:
        return json.loads(_STORE.read_text(encoding="utf-8"))
    except Exception:
        return {"rules": []}


def _save_store(data: Dict[str, Any]) -> None:
    _STORE.write_text(json.dumps(data, indent=2), encoding="utf-8")


# -------- CRUD --------

def list_rules() -> List[Dict[str, Any]]:
    return _load_store().get("rules", [])


def create_rule(rule: Dict[str, Any]) -> Dict[str, Any]:
    data = _load_store()
    rules = data.setdefault("rules", [])
    rid = rule.get("id") or f"al-{int(datetime.utcnow().timestamp()*1000)}"
    row = {"id": rid, "created_at": datetime.utcnow().isoformat(), **rule}
    rules.append(row)
    _save_store(data)
    return row


# -------- Evaluation --------
async def evaluate_once() -> Dict[str, Any]:
    rules = list_rules()
    triggered: List[Dict[str, Any]] = []
    for r in rules:
        rule = r.get("rule") or {}
        rtype = str(rule.get("type", "")).lower()
        try:
            if rtype in ("price_cross", "percent_move"):
                sym = rule.get("symbol")
                if not sym:
                    continue
                price = await _latest_price(sym)
                if price is None:
                    continue
                if rtype == "price_cross":
                    op = rule.get("op", ">")
                    thr = float(rule.get("threshold", math.nan))
                    if (op == ">" and price > thr) or (op == "<" and price < thr) or (op == ">=" and price >= thr) or (op == "<=" and price <= thr) or (op == "==" and price == thr):
                        triggered.append({"id": r.get("id"), "symbol": sym, "price": price, "type": rtype})
                else:  # percent_move
                    window = rule.get("window", "1d")
                    ref = await _ref_price(sym, window)
                    if ref is not None and ref != 0:
                        pct = (price - ref) / ref * 100.0
                        thr = float(rule.get("threshold", 0.0))
                        op = rule.get("op", ">=")
                        if (op == ">" and pct > thr) or (op == "<" and pct < thr) or (op == ">=" and pct >= thr) or (op == "<=" and pct <= thr):
                            triggered.append({"id": r.get("id"), "symbol": sym, "price": price, "pct": pct, "type": rtype})
        except Exception:
            continue
    return {"evaluated": len(rules), "triggered": triggered}


async def _latest_price(symbol: str) -> Optional[float]:
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="1d", interval="1m")
        if df is None or df.empty:
            df = t.history(period="5d", interval="5m")
        if df is None or df.empty:
            return None
        return float(df["Close"].iloc[-1])
    except Exception:
        return None


async def _ref_price(symbol: str, window: str) -> Optional[float]:
    try:
        t = yf.Ticker(symbol)
        if window.endswith("d"):
            days = int(window[:-1])
            period = f"{max(days, 1)}d"
            interval = "1h" if days <= 5 else "1d"
        elif window.endswith("h"):
            hours = int(window[:-1])
            period = "1d"
            interval = "5m" if hours <= 6 else "15m"
        else:
            period = "5d"
            interval = "1h"
        df = t.history(period=period, interval=interval)
        if df is None or df.empty:
            return None
        return float(df["Close"].iloc[0])
    except Exception:
        return None