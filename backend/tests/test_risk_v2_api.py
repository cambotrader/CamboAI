from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_risk_v2_summary():
    r = client.get("/api/v2/risk/summary", params={"symbol": "SPY"})
    assert r.status_code == 200
    body = r.json()
    assert "metrics" in body
    for k in ("volatility_annual", "max_drawdown", "var_95_daily", "es_95_daily", "sharpe"):
        assert k in body["metrics"]