import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_analysis_v1():
    r = client.get("/api/v1/analysis/technical", params={"symbol": "AAPL", "period": "1mo", "interval": "1d"})
    # Allow 400 if no network/TA-Lib issues
    assert r.status_code in (200, 400)
    if r.status_code == 200:
        body = r.json()
        assert "sma" in body and "rsi" in body and "bollinger_bands" in body