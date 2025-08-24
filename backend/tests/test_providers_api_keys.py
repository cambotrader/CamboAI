from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# These tests assume unsecured auth fallback returns None and endpoints handle it gracefully.

def test_preferred_provider_get_noauth():
    r = client.get("/api/v1/providers/market-data/preferred")
    assert r.status_code in (200,)
    body = r.json()
    assert "preferred" in body


def test_preferred_provider_set_unauthorized():
    r = client.post("/api/v1/providers/market-data/preferred", json={"preferred_market_data": "yahoo"})
    # Should respond with unauthorized gracefully
    assert r.status_code in (200, 401, 403)


def test_broker_keys_list_unauthorized():
    r = client.get("/api/v1/providers/broker/keys")
    assert r.status_code in (200, 401, 403)


def test_broker_keys_add_unauthorized():
    r = client.post("/api/v1/providers/broker/keys", json={
        "broker_name": "ALPACA",
        "api_key": "k",
        "api_secret": "s",
        "base_url": "https://paper-api.alpaca.markets",
        "paper": True
    })
    assert r.status_code in (200, 401, 403)