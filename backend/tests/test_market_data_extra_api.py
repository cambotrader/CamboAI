from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def _assert_series(resp):
    assert resp.status_code == 200
    body = resp.json()
    assert "symbol" in body and "provider" in body and "data" in body
    assert isinstance(body["data"], list)


def test_crypto_ohlcv():
    r = client.get("/api/v1/md/crypto/ohlcv", params={"symbol": "BTC-USD", "days": 10})
    _assert_series(r)


def test_fx_ohlcv():
    r = client.get("/api/v1/md/fx/ohlcv", params={"symbol": "EURUSD", "days": 10})
    _assert_series(r)


def test_options_ohlcv():
    r = client.get("/api/v1/md/options/ohlcv", params={"symbol": "AAPL230915C00175000", "days": 10})
    _assert_series(r)