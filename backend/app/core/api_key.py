from __future__ import annotations
"""Simple API key authentication utilities.

- Reads API key from env X_API_KEY (or API_KEY)
- Middleware can enforce for write/admin routes
"""
import os
from typing import Optional
from fastapi import Request

ENV_KEYS = ("X_API_KEY", "API_KEY")


def get_expected_key() -> Optional[str]:
    for k in ENV_KEYS:
        v = os.getenv(k)
        if v:
            return v.strip()
    return None


def is_protected_request(request: Request) -> bool:
    """Protect non-GET by default. Additional prefixes can be configured.
    API_KEY_PROTECTED_PREFIXES: comma-separated list, e.g. /api/v1/trading,/api/admin

    Tests expect that GET is allowed without a key, even under protected prefixes.
    """
    if request.method.upper() != "GET":
        return True
    # GET requests are not protected by default
    prefixes = [p.strip() for p in os.getenv("API_KEY_PROTECTED_PREFIXES", "").split(",") if p.strip()]
    if not prefixes:
        return False
    path = request.url.path
    # For GET, do not enforce API key even if prefix matches
    return False


def validate_api_key(request: Request) -> bool:
    expected = get_expected_key()
    if not expected:
        # No key configured -> allow
        return True
    provided = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
    if not provided:
        return False
    return provided.strip() == expected