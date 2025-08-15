from __future__ import annotations
import os
from typing import Optional

try:
    import redis
except Exception:
    redis = None

_redis_client = None

def get_redis() -> Optional["redis.Redis"]:
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    url = os.getenv("REDIS_URL")
    if not url or redis is None:
        return None
    _redis_client = redis.from_url(url, decode_responses=True)
    return _redis_client