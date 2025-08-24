from __future__ import annotations
from typing import Optional, Dict, Any
import os
import pandas as pd
import httpx

from app.services.redis_service import get_redis
from app.core.metrics import MetricsManager

class OptionsProvider:
    name = "options"

    def __init__(self):
        self.polygon_key = os.getenv("POLYGON_API_KEY")
        self.enable_polygon = os.getenv("ENABLE_POLYGON", "1").strip().lower() not in ("0", "false")
        self.cache_ttl_sec = int(os.getenv("MD_CACHE_TTL", "120"))

    def _cache_key(self, symbol: str, days: int) -> str:
        return f"md:options:{symbol}:{days}"

    def _from_polygon(self, symbol: str, days: int = 30) -> pd.DataFrame:
        if not (self.polygon_key and self.enable_polygon):
            return pd.DataFrame()
        try:
            poly_symbol = symbol
            if not poly_symbol.startswith("O:"):
                poly_symbol = f"O:{poly_symbol}"
            start_date = (pd.Timestamp.utcnow().date() - pd.Timedelta(days=days+1))
            end_date = pd.Timestamp.utcnow().date()
            url = (
                f"https://api.polygon.io/v2/aggs/ticker/{poly_symbol}/range/1/day/"
                f"{start_date}/{end_date}?adjusted=true&sort=asc&limit=5000&apiKey={self.polygon_key}"
            )
            for _ in range(2):
                try:
                    with httpx.Client(timeout=5.0) as client:
                        r = client.get(url)
                        if r.status_code != 200:
                            continue
                        data = r.json()
                        rows = data.get("results") or []
                        if not rows:
                            return pd.DataFrame()
                        df = pd.DataFrame(rows).rename(columns={
                            "t": "Date", "o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"
                        })
                        df["Date"] = pd.to_datetime(df["Date"], unit="ms")
                        df = df.set_index("Date").sort_index()
                        return df[["Open", "High", "Low", "Close", "Volume"]]
                except Exception:
                    continue
        except Exception:
            return pd.DataFrame()
        return pd.DataFrame()

    def fetch_ohlcv(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        rds = get_redis()
        key = self._cache_key(symbol, days)

        if rds is not None:
            try:
                cached = rds.get(key)
                if cached:
                    df = pd.read_json(cached, orient="split")
                    MetricsManager.record_cache_operation("md_options", True)
                    return {"df": df, "provider": "cache"}
                MetricsManager.record_cache_operation("md_options", False)
            except Exception:
                pass

        df = self._from_polygon(symbol, days)
        provider = "polygon" if isinstance(df, pd.DataFrame) and not df.empty else None

        if rds is not None and isinstance(df, pd.DataFrame) and not df.empty:
            try:
                rds.setex(key, self.cache_ttl_sec, df.to_json(orient="split"))
            except Exception:
                pass

        return {"df": df if isinstance(df, pd.DataFrame) else pd.DataFrame(), "provider": provider or "synthetic"}

_singleton: Optional[OptionsProvider] = None

def get_options_provider() -> OptionsProvider:
    global _singleton
    if _singleton is None:
        _singleton = OptionsProvider()
    return _singleton