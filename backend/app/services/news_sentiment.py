from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import time
import html
import re
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

# Free-first aggregator for headlines + naive sentiment.
# Sources supported now (no paid keys): Yahoo Finance (HTML), Google News (RSS), Reddit (public JSON/HTML best-effort).
# Designed to be extended with API-based providers when keys are available (Benzinga, Finnhub, NewsAPI, etc.).

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

# Simple in-memory TTL cache to reduce request load and rate limits
_CACHE: Dict[str, Tuple[float, Any]] = {}
_CACHE_TTL_SEC = 120  # 2 minutes


def _cache_get(key: str):
    row = _CACHE.get(key)
    if not row:
        return None
    ts, data = row
    if time.time() - ts > _CACHE_TTL_SEC:
        return None
    return data


def _cache_set(key: str, data: Any):
    _CACHE[key] = (time.time(), data)


# --------------------------- Sentiment Scoring ---------------------------
NEG = {"falls", "drop", "decline", "plunge", "slump", "bear", "loss", "risk", "fear", "selloff", "miss", "cut", "downgrade", "lawsuit", "ban"}
POS = {"rises", "gain", "rally", "surge", "jump", "bull", "beat", "strong", "soar", "up", "upgrade", "record"}


def _score_title(title: str) -> float:
    t = title.lower()
    # basic lexicon scoring
    neg = sum(1 for w in NEG if w in t)
    pos = sum(1 for w in POS if w in t)
    if pos == neg == 0:
        return 0.0
    return (pos - neg) / max(1, (pos + neg))


def _annotate(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for it in items:
        s = _score_title(it.get("title", ""))
        it["score"] = round(s, 2)
        it["tone"] = "🟢" if s > 0.15 else "🔴" if s < -0.15 else "⚪"
        out.append(it)
    return out


# --------------------------- Fetchers ---------------------------

def _fetch_yahoo(symbol: Optional[str], limit: int) -> List[Dict[str, Any]]:
    url = "https://finance.yahoo.com/" if not symbol else f"https://finance.yahoo.com/quote/{symbol}"
    key = f"yahoo::{symbol or 'home'}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    try:
        html_text = requests.get(url, headers=UA, timeout=10).text
        soup = BeautifulSoup(html_text, "html.parser")
        items = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not isinstance(href, str) or "/news/" not in href:
                continue
            title = a.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            items.append({
                "source": "Yahoo",
                "title": title,
                "url": ("https://finance.yahoo.com" + href) if href.startswith("/") else href,
                "t": datetime.utcnow().isoformat(),
            })
            if len(items) >= limit:
                break
        _cache_set(key, items)
        return items
    except Exception:
        return []


def _fetch_google_news(symbol: Optional[str], limit: int) -> List[Dict[str, Any]]:
    # Use Google News RSS to avoid heavy HTML parsing.
    query = "markets" if not symbol else f"{symbol} stock"
    url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    key = f"gnews::{query}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    try:
        resp = requests.get(url, headers=UA, timeout=10)
        resp.raise_for_status()
        items: List[Dict[str, Any]] = []
        root = ET.fromstring(resp.text)
        # RSS structure: channel/item
        for item in root.findall(".//item"):
            title_el = item.find("title")
            link_el = item.find("link")
            pub_el = item.find("pubDate")
            title = html.unescape(title_el.text) if title_el is not None else ""
            link = (link_el.text or "") if link_el is not None else ""
            t = datetime.utcnow().isoformat() if pub_el is None else pub_el.text
            if not title:
                continue
            items.append({
                "source": "GoogleNews",
                "title": title,
                "url": link,
                "t": t,
            })
            if len(items) >= limit:
                break
        _cache_set(key, items)
        return items
    except Exception:
        return []


def _fetch_reddit(symbol: Optional[str], limit: int) -> List[Dict[str, Any]]:
    # Best-effort using public JSON search on popular finance subs.
    subs = ["stocks", "wallstreetbets", "investing"]
    query = "markets" if not symbol else symbol
    items: List[Dict[str, Any]] = []
    for sub in subs:
        try:
            url = f"https://www.reddit.com/r/{sub}/search.json?q={requests.utils.quote(query)}&restrict_sr=1&sort=new&t=day"
            r = requests.get(url, headers=UA, timeout=10)
            if r.status_code != 200:
                continue
            data = r.json()
            for child in (data.get("data", {}).get("children", []) or []):
                d = child.get("data", {})
                title = d.get("title")
                permalink = d.get("permalink")
                if not title or not permalink:
                    continue
                items.append({
                    "source": f"Reddit/{sub}",
                    "title": title,
                    "url": f"https://www.reddit.com{permalink}",
                    "t": datetime.utcfromtimestamp(d.get("created_utc", time.time())).isoformat(),
                })
                if len(items) >= limit:
                    break
        except Exception:
            continue
        if len(items) >= limit:
            break
    return items


# --------------------------- Public API ---------------------------

from .feeds import bundle_feeds

FREE_SOURCES = {
    "yahoo": _fetch_yahoo,
    "google": _fetch_google_news,
    "reddit": _fetch_reddit,
    "macro_feeds": lambda symbol, limit: bundle_feeds(limit_per=max(3, limit // 6)),
}


def headlines(symbol: Optional[str] = None, sources: Optional[List[str]] = None, limit: int = 25) -> Dict[str, Any]:
    srcs = sources or list(FREE_SOURCES.keys())
    all_items: List[Dict[str, Any]] = []
    for key in srcs:
        fn = FREE_SOURCES.get(key)
        if not fn:
            continue
        all_items.extend(fn(symbol, limit=max(5, limit // len(srcs))))
    # de-duplicate by title+url
    seen = set()
    dedup: List[Dict[str, Any]] = []
    for it in all_items:
        sig = (it.get("title"), it.get("url"))
        if sig in seen:
            continue
        seen.add(sig)
        dedup.append(it)
    dedup.sort(key=lambda x: x.get("t", ""), reverse=True)
    return {"items": _annotate(dedup)[:limit]}


def sentiment_summary(symbol: Optional[str] = None, sources: Optional[List[str]] = None, limit: int = 50) -> Dict[str, Any]:
    data = headlines(symbol, sources=sources, limit=limit)
    items = data.get("items", [])
    if not items:
        return {"symbol": symbol, "score": 0.0, "label": "Neutral", "history": []}
    scores = [it.get("score", 0.0) for it in items]
    avg = sum(scores) / max(1, len(scores))
    label = "Bullish" if avg > 0.15 else "Bearish" if avg < -0.15 else "Neutral"
    # trailing history
    hist = [round(s, 2) for s in scores[:20]]
    return {"symbol": symbol, "score": round(avg, 2), "label": label, "history": hist, "count": len(items)}