from __future__ import annotations
from typing import Dict, Any, Optional, List

from . import patterns as patterns_service
from . import news_sentiment as sentiment_service

# Simple weights mapping based on detection name substrings
WEIGHTS = [
    ("bullish engulfing", 1.2),
    ("bearish engulfing", -1.2),
    ("hammer", 0.8),
    ("shooting star", -0.8),
    ("morning star", 1.0),
    ("evening star", -1.0),
    ("momentum burst", 0.5),
    ("momentum neutral", 0.0),
]


def _pattern_score(detections: List[Dict[str, Any]]) -> float:
    score = 0.0
    for d in detections[-8:]:  # last few
        name = str(d.get("name", "")).lower()
        conf = float(d.get("confidence", 0.5))
        applied = False
        for key, w in WEIGHTS:
            if key in name:
                score += w * conf
                applied = True
                break
        if not applied:
            # Try direction in extra
            direction = str(d.get("extra", {}).get("direction", "")).lower()
            if direction == "bullish":
                score += 0.4 * conf
            elif direction == "bearish":
                score -= 0.4 * conf
    # soft clip
    if score > 3:
        score = 3
    if score < -3:
        score = -3
    return score


def _label_from_score(norm: float) -> str:
    if norm > 0.25:
        return "BUY"
    if norm < -0.25:
        return "SELL"
    return "NEUTRAL"


def generate_signal(symbol: Optional[str], timeframe: str = "1D", period: str = "6mo") -> Dict[str, Any]:
    """Generate fused signal for symbol using internal services.
    Robust to data/sentiment failures (returns NEUTRAL on errors).
    """
    try:
        patt = patterns_service.scan(symbol or "SPY", timeframe=timeframe, period=period)
    except Exception:
        patt = {"detections": [], "context": {}}

    detections = patt.get("detections", []) or []
    p_score = _pattern_score(detections)

    try:
        sent = sentiment_service.sentiment_summary(symbol, limit=30)
        s_score = float(sent.get("score", 0.0))  # already in ~[-1,1]
    except Exception:
        s_score = 0.0

    raw = p_score + 0.7 * s_score
    norm = max(-1.0, min(1.0, raw / 3.7))
    label = _label_from_score(norm)

    return {
        "symbol": symbol,
        "label": label,
        "score": round(norm, 3),
        "confidence": round(abs(norm), 3),
        "detail": {
            "pattern_score": round(p_score, 3),
            "sentiment": round(s_score, 3),
            "timeframe": timeframe,
            "period": period,
            "detections": detections[:10],
        },
    }