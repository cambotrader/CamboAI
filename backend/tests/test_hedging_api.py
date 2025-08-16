import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_delta_hedge_endpoint():
    payload = {"spot": 100, "vol": 0.2, "rate": 0.01, "t": 0.5, "strike": 100, "right": "call"}
    r = client.post("/api/options/hedging/delta", json=payload)
    assert r.status_code == 200
    j = r.json()
    assert "total_pnl" in j and "final_underlying" in j