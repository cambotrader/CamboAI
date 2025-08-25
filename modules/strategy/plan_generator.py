"""Trade Plan Generator (MVP)

Composes a structured trade plan from strategy & pattern signals and sentiment snapshot(s).
Later expansions: options overlays, risk modeling, scenario branching.
"""
from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime
from modules.models import StrategySignal, PatternDetection, SentimentSnapshot
from modules.strategy.position_sizing import position_size


def generate_trade_plan(symbol: str, strategy_signals: List[StrategySignal], patterns: List[PatternDetection], sentiment: List[SentimentSnapshot], df=None, account_equity: float = 25_000.0, risk_fraction: float = 0.01) -> Dict[str, Any]:
    bullish = [s for s in strategy_signals if s.direction == "long"]
    bearish = [s for s in strategy_signals if s.direction == "short"]
    net_bias = (len(bullish) - len(bearish))
    bias_label = "bullish" if net_bias > 0 else "bearish" if net_bias < 0 else "neutral"

    avg_conf = 0.0
    all_conf = [s.confidence for s in strategy_signals]
    if all_conf:
        avg_conf = sum(all_conf) / len(all_conf)

    latest_sent = sentiment[-1] if sentiment else None
    sentiment_label = latest_sent.label if latest_sent else "unknown"

    rationale_parts = []
    if bullish:
        rationale_parts.append(f"{len(bullish)} long signals")
    if bearish:
        rationale_parts.append(f"{len(bearish)} short signals")
    if patterns:
        rationale_parts.append(f"{len(patterns)} patterns active")
    if latest_sent:
        rationale_parts.append(f"sentiment {sentiment_label}")
    rationale = ", ".join(rationale_parts) or "No actionable signals yet"

    # Simple SL/TP heuristic (placeholder)
    risk_reward = 2.0
    sizing = position_size(account_equity, df) if df is not None else {}
    plan = {
        "symbol": symbol,
        "timestamp": datetime.utcnow().isoformat(),
        "bias": bias_label,
        "confidence_avg": round(avg_conf, 3),
        "sentiment": sentiment_label,
        "rationale": rationale,
        "risk_reward_target": risk_reward,
        "position_sizing": sizing,
        "notes": "MVP plan; refine with volatility, multi-timeframe confluence & options later.",
    }
    return plan

__all__ = ["generate_trade_plan"]
