"""FinBERT Sentiment Stub

Placeholder until real model integration. Provides a deterministic, lexicon-based
approximation returning scores + label consistent with expected interface.
"""
from __future__ import annotations

from typing import Dict, List
import math

POS_WORDS = {"beat", "growth", "surge", "win", "strong", "bull", "upgrade"}
NEG_WORDS = {"miss", "drop", "loss", "weak", "bear", "downgrade", "fraud"}


def score_text(text: str) -> Dict[str, float]:
    tokens = [t.lower().strip(".,!?;:") for t in text.split()]
    pos = sum(1 for t in tokens if t in POS_WORDS)
    neg = sum(1 for t in tokens if t in NEG_WORDS)
    total = max(1, pos + neg)
    pos_s = pos / total
    neg_s = neg / total
    neu_s = max(0.0, 1 - (pos_s + neg_s))
    return {"positive": pos_s, "negative": neg_s, "neutral": neu_s}


def label(scores: Dict[str, float]) -> str:
    k = max(scores, key=scores.get)
    return k


def summarize(headlines: List[str]) -> Dict[str, float]:
    if not headlines:
        return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
    agg = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    for h in headlines:
        s = score_text(h)
        for k, v in s.items():
            agg[k] += v
    n = len(headlines)
    for k in agg:
        agg[k] /= n
    # Normalize just in case
    s = sum(agg.values()) or 1.0
    for k in agg:
        agg[k] /= s
    return agg


__all__ = ["score_text", "label", "summarize"]
