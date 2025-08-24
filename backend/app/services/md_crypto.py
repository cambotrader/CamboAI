from __future__ import annotations
from typing import Optional, Dict, Any
import os
import pandas as pd
import yfinance as yf
import httpx

from app.services.redis_service import get_redis
from app.core.metrics import MetricsManager

class CryptoProvider:
    name = "crypto"

    def __init__(self):
        # Feature flags
        self.enable_polygon = os.getenv("ENABLE_POLYGON", "1").strip().lower() not in ("0", "false")
        self.enable_yahoo = os.getenv("ENABLE_YAHOO", "1").strip().lower() not in ("0", "false")
        # Keys
        self.polygon_key = os.getenv("POLYGON_API_KEY")
        self.tiingo_key = os.getenv("TIINGO_API_KEY")
        # Caching
        self.cache_ttl_sec = int(os.getenv("MD_CACHE_TTL", "120"))

    def _cache_key(self, symbol: str, days: int) -> str:
        return f"md:crypto:{symbol}:{days}"

    def _from_yf(self, symbol: str, days: int = 30) -> pd.DataFrame:
        if not self.enable_yahoo:
            return pd.DataFrame()
        try:
            df = yf.Ticker(symbol).history(period=f"{max(1, days)}d", interval="1d")
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df[["Open", "High", "Low", "Close", "Volume"]]
        except Exception:
            pass
        return pd.DataFrame()

    def _from_polygon(self, symbol: str, days: int = 30) -> pd.DataFrame:
        if not (self.enable_polygon and self.polygon_key):
            return pd.DataFrame()
        try:
            poly_symbol = symbol.replace("-", "")
            if poly_symbol.endswith("USD"):
                poly_symbol = f"X:{poly_symbol}"
            start = (pd.Timestamp.utcnow().date() - pd.Timedelta(days=days + 1))
            end = pd.Timestamp.utcnow().date()
            url = (
                f"https://api.polygon.io/v2/aggs/ticker/{poly_symbol}/range/1/day/{start}/{end}"
                f"?adjusted=true&sort=asc&limit=5000&apiKey={self.polygon_key}"
            )
            # Basic retry x2
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

        # Cache read
        if rds is not None:
            try:
                cached = rds.get(key)
                if cached:
                    df = pd.read_json(cached, orient="split")
                    MetricsManager.record_cache_operation("md_crypto", True)
                    return {"df": df, "provider": "cache"}
                MetricsManager.record_cache_operation("md_crypto", False)
            except Exception:
                pass

        # Try Polygon, then Yahoo
        df = self._from_polygon(symbol, days)
        provider = "polygon" if isinstance(df, pd.DataFrame) and not df.empty else None
        if df is None or df.empty:
            df = self._from_yf(symbol, days)
            if isinstance(df, pd.DataFrame) and not df.empty:
                provider = "yahoo"

        # Cache write
        if rds is not None and isinstance(df, pd.DataFrame) and not df.empty:
            try:
                rds.setex(key, self.cache_ttl_sec, df.to_json(orient="split"))
            except Exception:
                pass

        return {"df": df if isinstance(df, pd.DataFrame) else pd.DataFrame(), "provider": provider or "synthetic"}

_singleton: Optional[CryptoProvider] = None

def get_crypto_provider() -> CryptoProvider:
    global _singleton
    if _singleton is None:
        _singleton = CryptoProvider()
    return _singleton