import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_risk_summary_v1():
    r = client.get("/api/v1/risk/summary", params={"symbol": "SPY"})
    assert r.status_code == 200
    body = r.json()
    assert "risk_metrics" in body
    rm = body["risk_metrics"]
    assert all(k in rm for k in ("volatility", "maximum_drawdown", "sharpe_ratio", "value_at_risk_95"))