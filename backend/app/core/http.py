from __future__ import annotations
"""
Robust HTTP utilities: timeouts, retries with backoff, request-id propagation,
and simple circuit breaker. Uses httpx for sync requests (can be extended to async).
"""
import os
import time
import uuid
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

import httpx

from .metrics import MetricsManager

DEFAULT_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "6.0"))
DEFAULT_RETRIES = int(os.getenv("HTTP_RETRIES", "2"))
DEFAULT_BACKOFF = float(os.getenv("HTTP_BACKOFF", "0.5"))  # seconds base
CB_FAIL_THRESHOLD = int(os.getenv("HTTP_CB_FAILS", "5"))
CB_RESET_SECONDS = float(os.getenv("HTTP_CB_RESET", "30.0"))


@dataclass
class CircuitState:
    failures: int = 0
    opened_at: float = 0.0


class CircuitBreaker:
    """Simple circuit breaker per service key."""

    def __init__(self):
        self._states: Dict[str, CircuitState] = {}

    def is_open(self, key: str) -> bool:
        st = self._states.get(key)
        if not st:
            return False
        if st.failures < CB_FAIL_THRESHOLD:
            return False
        # open until reset window elapses
        return (time.time() - st.opened_at) < CB_RESET_SECONDS

    def report_success(self, key: str):
        self._states[key] = CircuitState(0, 0.0)

    def report_failure(self, key: str):
        st = self._states.get(key) or CircuitState()
        st.failures += 1
        if st.failures >= CB_FAIL_THRESHOLD:
            st.opened_at = time.time()
        self._states[key] = st


_cb = CircuitBreaker()


def _request_id() -> str:
    return uuid.uuid4().hex


def request(
    method: str,
    url: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[dict] = None,
    params: Optional[dict] = None,
    timeout: float = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    backoff: float = DEFAULT_BACKOFF,
    service_key: Optional[str] = None,
) -> Tuple[int, str | bytes, httpx.Response | None]:
    """
    Perform an HTTP request with retry/backoff and circuit breaker.
    Returns: (status_code, text_or_bytes, response)
    """
    key = service_key or url.split("/")[2] if "://" in url else (service_key or "service")

    # Circuit breaker check
    if _cb.is_open(key):
        MetricsManager.record_api_error(url, "circuit_open")
        return 503, "circuit_open", None

    req_id = _request_id()
    hdrs = {"X-Request-ID": req_id, **(headers or {})}

    last_exc: Optional[Exception] = None
    start = time.perf_counter()
    for attempt in range(retries + 1):
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.request(method, url, headers=hdrs, json=json, params=params)
            elapsed = time.perf_counter() - start
            MetricsManager.record_request(method.upper(), url, resp.status_code, elapsed)
            if resp.status_code >= 500:
                # retry on server errors
                _cb.report_failure(key)
                if attempt < retries:
                    time.sleep(backoff * (2 ** attempt))
                    continue
            else:
                # success or client error ends attempts
                _cb.report_success(key)
            return resp.status_code, resp.text, resp
        except Exception as exc:  # network/timeout
            last_exc = exc
            _cb.report_failure(key)
            if attempt < retries:
                time.sleep(backoff * (2 ** attempt))
                continue

    elapsed = time.perf_counter() - start
    MetricsManager.record_api_error(url, type(last_exc).__name__ if last_exc else "error")
    return 0, str(last_exc) if last_exc else "error", None