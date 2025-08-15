from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime
import html
import requests
import xml.etree.ElementTree as ET

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

# A few high-value free RSS feeds. Extend as needed.
FEEDS: Dict[str, str] = {
    "SEC_Press": "https://www.sec.gov/news/pressreleases.rss",
    "SEC_PublicStatements": "https://www.sec.gov/news/public-statements.rss",
    "FED_Press": "https://www.federalreserve.gov/feeds/press_all.xml",
    "ECB_Press": "https://www.ecb.europa.eu/press/pressconf/pressconf.rss",
    "IMF_News": "https://www.imf.org/en/News/Articles/rss",
    "WorldBank_News": "https://www.worldbank.org/en/news/all?format=rss",
    "BIS_News": "https://www.bis.org/list/press_releases/page.htm?channel=rss",
}


def fetch_rss(url: str, limit: int = 20) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    try:
        resp = requests.get(url, headers=UA, timeout=12)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
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
                "source": url,
                "title": title,
                "url": link,
                "t": t,
            })
            if len(items) >= limit:
                break
    except Exception:
        return []
    return items


def bundle_feeds(limit_per: int = 10) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for name, url in FEEDS.items():
        rows = fetch_rss(url, limit=limit_per)
        for r in rows:
            r["source"] = name
            out.append(r)
    # sort newest first if pubDate parseable; fallback to order
    return out