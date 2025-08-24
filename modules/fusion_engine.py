"""
Fusion Engine: Combines pattern_engine outputs with sentiment to produce
an actionable signal with a confidence score.

Inputs:
- patterns: list of PatternSignal-like dicts (from pattern_engine.analyze)
- sentiment_score: float in [-1, 1] (negative = bearish, positive = bullish)

Output:
- dict: { label: BUY|SELL|NEUTRAL, score: -1..1, confidence: 0..1, detail: {...} }
"""
from __future__ import annotations

from typing import List, Dict, Any


WEIGHTS = {
    "golden_cross": 1.5,
    "death_cross": -1.5,
    "bullish_engulfing": 1.0,
    "bearish_engulfing": -1.0,
    "hammer": 0.8,
    "shooting_star": -0.8,
    "rsi_oversold": 0.5,
    "rsi_overbought": -0.5,
    "doji": 0.0,
}


def _pattern_score(patterns: List[Dict[str, Any]]) -> float:
    score = 0.0
    contributions = []
    for p in patterns:
        ptype = p.get("type")
        w = WEIGHTS.get(ptype, 0.0)
        # Directionless patterns (e.g., doji) get near-zero contribution
        # Confidence scales the weight linearly
        conf = float(p.get("confidence", 0.5))
        s = w * conf
        score += s
        contributions.append({"type": ptype, "weight": w, "confidence": conf, "contrib": s})
    # Soft clip (not strictly necessary, just keep reasonable range)
    if score > 3:
        score = 3
    if score < -3:
        score = -3
    return score


def fuse(patterns: List[Dict[str, Any]], sentiment_score: float) -> Dict[str, Any]:
    # Normalize sentiment to [-1, 1]
    try:
        s = max(-1.0, min(1.0, float(sentiment_score)))
    except Exception:
        s = 0.0

    p_score = _pattern_score(patterns)
    # Combine: patterns dominate slightly, sentiment augments.
    raw = p_score + 0.7 * s

    # Normalize to [-1, 1] by dividing by a constant (max expected magnitude ~3.7)
    norm = max(-1.0, min(1.0, raw / 3.7))

    if norm > 0.25:
        label = "BUY"
    elif norm < -0.25:
        label = "SELL"
    else:
        label = "NEUTRAL"

    return {
        "label": label,
        "score": norm,
        "confidence": abs(norm),
        "detail": {
            "pattern_score": p_score,
            "sentiment": s,
            "raw": raw,
        }
    }