# news_sentiment.py - CamboAI sentiment panel
# Pulls headlines via yfinance (fallback list if unavailable) and scores sentiment.
# Tries FinBERT if installed; otherwise uses a simple keyword heuristic.

from __future__ import annotations
from typing import List, Dict
from datetime import datetime

import pandas as pd

try:
    import yfinance as yf
except Exception:
    yf = None

# Optional FinBERT
_finbert_ready = False
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification  # type: ignore
    import torch  # type: ignore
    _tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    _model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    _labels = ["negative", "neutral", "positive"]
    _finbert_ready = True
except Exception:
    _tokenizer = None
    _model = None
    _labels = ["negative", "neutral", "positive"]


def _finbert_score(text: str) -> str:
    if not _finbert_ready:
        return "neutral"
    inputs = _tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = _model(**inputs)
    scores = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
    idx = int(scores.argmax())
    return _labels[idx]


_HEURISTICS = {
    "positive": ["beat", "surge", "record", "up", "growth", "gain", "partnership", "upgrade"],
    "negative": ["miss", "down", "lawsuit", "probe", "layoff", "fraud", "downgrade", "drop"],
}


def _heuristic_score(text: str) -> str:
    t = text.lower()
    pos = any(w in t for w in _HEURISTICS["positive"])
    neg = any(w in t for w in _HEURISTICS["negative"])
    if pos and not neg:
        return "positive"
    if neg and not pos:
        return "negative"
    return "neutral"


def get_headlines(ticker: str, limit: int = 6) -> List[Dict]:
    items: List[Dict] = []
    if yf is not None:
        try:
            news = yf.Ticker(ticker).news[:limit]
            for n in news:
                items.append({
                    "title": n.get("title", ""),
                    "link": n.get("link", ""),
                    "publisher": n.get("publisher", ""),
                    "time": pd.to_datetime(n.get("providerPublishTime", datetime.utcnow()), unit="s", errors="coerce"),
                })
        except Exception:
            pass

    if not items:
        # Fallback sample
        now = pd.Timestamp.utcnow()
        items = [
            {"title": f"{ticker.upper()} announces AI partnership", "link": "", "publisher": "Wire", "time": now},
            {"title": f"{ticker.upper()} faces regulatory probe", "link": "", "publisher": "Wire", "time": now - pd.Timedelta(days=2)},
            {"title": f"{ticker.upper()} Q2 earnings exceed expectations", "link": "", "publisher": "Wire", "time": now - pd.Timedelta(days=4)},
        ][:limit]
    return items


def score_headlines(items: List[Dict]) -> List[Dict]:
    scored = []
    for it in items:
        title = it.get("title", "")
        tone = _finbert_score(title) if _finbert_ready else _heuristic_score(title)
        emoji = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}.get(tone, "🟡")
        scored.append({
            **it,
            "tone": tone,
            "emoji": emoji,
        })
    return scored


def build_sentiment_zones(items: List[Dict]):
    zones = []
    color = {"positive": "rgba(0,200,0,0.18)", "neutral": "rgba(200,200,0,0.18)", "negative": "rgba(200,0,0,0.18)"}
    for it in items:
        t = it.get("time", pd.Timestamp.utcnow())
        tone = it.get("tone", "neutral")
        zones.append({
            "start": t - pd.Timedelta(days=1),
            "end": t + pd.Timedelta(days=1),
            "color": color.get(tone, color["neutral"]),
            "label": tone,
        })
    return zones