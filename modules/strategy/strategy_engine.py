"""Strategy Engine Scaffold

Responsibilities:
1. Register strategies (simple callable objects) producing StrategySignal instances.
2. Provide evaluate(symbol, data, context) -> list[StrategySignal].
3. Allow strategy enable/disable flags.

This is an MVP; advanced items (portfolio context, risk overlays, ML inference)
will be layered later.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd

from modules.models import StrategySignal


StrategyFunc = Callable[[str, pd.DataFrame, Dict[str, Any]], List[StrategySignal]]


@dataclass
class RegisteredStrategy:
    name: str
    fn: StrategyFunc
    enabled: bool = True
    meta: Dict[str, Any] = field(default_factory=dict)


_REGISTRY: Dict[str, RegisteredStrategy] = {}


def register(name: str, fn: StrategyFunc, **meta):
    if name in _REGISTRY:
        raise ValueError(f"Strategy '{name}' already registered")
    _REGISTRY[name] = RegisteredStrategy(name=name, fn=fn, meta=meta)


def list_strategies(enabled_only: bool = True) -> List[str]:
    return [n for n, rs in _REGISTRY.items() if rs.enabled or not enabled_only]


def enable(name: str, value: bool = True):
    if name in _REGISTRY:
        _REGISTRY[name].enabled = value


def evaluate(symbol: str, df: pd.DataFrame, context: Dict[str, Any] | None = None) -> List[StrategySignal]:
    context = context or {}
    out: List[StrategySignal] = []
    for name, rs in _REGISTRY.items():
        if not rs.enabled:
            continue
        try:
            signals = rs.fn(symbol, df, context)
            out.extend(signals)
        except Exception as e:  # noqa: BLE001
            # Fail soft; attach error meta signal
            out.append(StrategySignal(symbol=symbol, direction="flat", confidence=0.0, source=name, meta={"error": str(e)}))
    return out


# --- Built-in example strategies (MVP) ---
def _ma_crossover(symbol: str, df: pd.DataFrame, context: Dict[str, Any]) -> List[StrategySignal]:
    if len(df) < 50:
        return []
    close = df["Close"] if "Close" in df.columns else df.iloc[:, 0]
    ma_fast = close.rolling(20).mean()
    ma_slow = close.rolling(50).mean()
    if ma_fast.iloc[-2] <= ma_slow.iloc[-2] and ma_fast.iloc[-1] > ma_slow.iloc[-1]:
        return [StrategySignal(symbol=symbol, direction="long", confidence=0.7, source="ma_crossover", tags=["bullish", "ma"])]
    if ma_fast.iloc[-2] >= ma_slow.iloc[-2] and ma_fast.iloc[-1] < ma_slow.iloc[-1]:
        return [StrategySignal(symbol=symbol, direction="short", confidence=0.7, source="ma_crossover", tags=["bearish", "ma"])]
    return []


def _rsi_reversion(symbol: str, df: pd.DataFrame, context: Dict[str, Any]) -> List[StrategySignal]:
    if "Close" not in df.columns or len(df) < 15:
        return []
    close = df["Close"]
    rsi_period = context.get("rsi_period", 14)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/rsi_period, min_periods=rsi_period).mean()
    avg_loss = loss.ewm(alpha=1/rsi_period, min_periods=rsi_period).mean()
    rs = avg_gain / (avg_loss.replace(0, 1e-9))
    rsi = 100 - (100 / (1 + rs))
    last = rsi.iloc[-1]
    if last < 30:
        return [StrategySignal(symbol=symbol, direction="long", confidence=0.55, source="rsi_reversion", tags=["mean_revert"], meta={"rsi": float(last)})]
    if last > 70:
        return [StrategySignal(symbol=symbol, direction="short", confidence=0.55, source="rsi_reversion", tags=["mean_revert"], meta={"rsi": float(last)})]
    return []


# Register built-ins
register("ma_crossover", _ma_crossover, description="20/50 EMA crossover")
register("rsi_reversion", _rsi_reversion, description="RSI overbought/oversold reversal")

__all__ = [
    "register",
    "evaluate",
    "enable",
    "list_strategies",
]
