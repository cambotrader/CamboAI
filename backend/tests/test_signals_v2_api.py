from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_signals_v2_endpoint():
    r = client.get("/api/v2/signals", params={"symbol": "AAPL", "period": "1mo", "interval": "1d"})
    assert r.status_code in (200,)
    body = r.json()
    assert body["label"] in ("BUY", "SELL", "NEUTRAL")
    assert "version" in body and body["version"].startswith("v2")