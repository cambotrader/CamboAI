import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_alerts_crud_and_run():
    # List initially
    r = client.get("/api/alerts/rules")
    assert r.status_code == 200
    # Create one
    payload = {
        "rule": {"type": "price_cross", "symbol": "AAPL", "op": ">", "threshold": 200},
        "active": True
    }
    r = client.post("/api/alerts/rules", json=payload)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    # Run
    r = client.post("/api/alerts/run")
    assert r.status_code == 200
    data = r.json()
    assert "evaluated" in data