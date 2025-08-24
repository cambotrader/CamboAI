import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_signals_no_symbol():
    r = client.get("/api/v1/signals")
    assert r.status_code == 200
    body = r.json()
    assert "label" in body
    assert "score" in body
    assert "detail" in body


def test_signals_with_symbol():
    r = client.get("/api/v1/signals", params={"symbol": "AAPL", "timeframe": "1D", "period": "1mo"})
    assert r.status_code == 200
    body = r.json()
    assert body.get("symbol") in ("AAPL", None)
    assert body.get("label") in ("BUY", "SELL", "NEUTRAL")