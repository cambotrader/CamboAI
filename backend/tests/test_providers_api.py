from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_set_preferred_provider_unauthorized():
    r = client.post("/api/v1/providers/market-data/preferred", json={"preferred_market_data": "yahoo"})
    assert r.status_code in (401, 403)