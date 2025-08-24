from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import os
import time
import json
import numpy as np
import httpx

from .redis_service import get_redis


@dataclass
class SentimentDoc:
    id: str
    source: str
    title: str
    text: str
    url: Optional[str]
    timestamp: Optional[str]

@dataclass
class SentimentResult:
    score: float  # -1..1
    label: str    # BEARISH/NEUTRAL/BULLISH
    detail: Dict[str, Any]


class FinBERTClient:
    """Thin HTTP client to a FinBERT-compatible endpoint.
    Expected env: FINBERT_URL. If missing/unreachable, returns neutral.
    """

    def __init__(self, url: Optional[str] = None, timeout: float = 3.0):
        self.url = url or os.getenv("FINBERT_URL")
        self.timeout = timeout

    def analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        if not self.url or not texts:
            return [{"label": "neutral", "score": 0.0} for _ in texts]
        try:
            payload = {"texts": texts}
            with httpx.Client(timeout=self.timeout) as client:
                r = client.post(self.url.rstrip("/") + "/analyze", json=payload)
                if r.status_code != 200:
                    return [{"label": "neutral", "score": 0.0} for _ in texts]
                return r.json()
        except Exception:
            return [{"label": "neutral", "score": 0.0} for _ in texts]


class SentimentAggregatorV2:
    def __init__(self):
        self.client = FinBERTClient()
        self.cache_ttl = int(os.getenv("SENTIMENT_CACHE_TTL", "120"))

    def _label_to_score(self, label: str, score: float) -> float:
        l = (label or "").lower()
        if l.startswith("bull"):  # bullish
            return min(1.0, max(0.0, score))
        if l.startswith("bear"):  # bearish
            return -min(1.0, max(0.0, score))
        return 0.0

    def aggregate(self, docs: List[SentimentDoc]) -> SentimentResult:
        rds = get_redis()
        cache_key = None
        if rds is not None:
            try:
                cache_key = "sent:v2:" + str(hash("|".join(sorted(d.title for d in docs))))
                cached = rds.get(cache_key)
                if cached:
                    obj = json.loads(cached)
                    return SentimentResult(**obj)
            except Exception:
                pass

        texts = [d.title + "\n" + (d.text or "") for d in docs]
        preds = self.client.analyze(texts)
        scores = [self._label_to_score(p.get("label", "neutral"), float(p.get("score", 0.0))) for p in preds]
        score = float(np.tanh(np.mean(scores) * 1.5)) if scores else 0.0
        label = "BULLISH" if score > 0.2 else ("BEARISH" if score < -0.2 else "NEUTRAL")
        res = SentimentResult(score=score, label=label, detail={
            "sources": [d.source for d in docs],
            "count": len(docs),
            "scores": scores[:10],
        })

        if rds is not None and cache_key is not None:
            try:
                rds.setex(cache_key, self.cache_ttl, json.dumps(res.__dict__))
            except Exception:
                pass
        return res


_sent_singleton: Optional[SentimentAggregatorV2] = None

def get_sentiment_v2() -> SentimentAggregatorV2:
    global _sent_singleton
    if _sent_singleton is None:
        _sent_singleton = SentimentAggregatorV2()
    return _sent_singleton