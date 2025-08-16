import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_presets():
    r = client.get("/api/options/presets")
    assert r.status_code == 200
    data = r.json()
    assert "balanced" in data


def test_price_multi_leg_basic():
    payload = {
        "preset": "balanced",
        "legs": [
            {
                "right": "call", "side": "long", "qty": 1,
                "strike": 100, "expiry": 0.5, "vol": 0.2,
                "rate": 0.01, "div_yield": 0.0, "spot": 105
            },
            {
                "right": "call", "side": "short", "qty": 1,
                "strike": 110, "expiry": 0.5, "vol": 0.2,
                "rate": 0.01, "div_yield": 0.0, "spot": 105
            }
        ]
    }
    r = client.post("/api/options/price/multi-leg", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "price" in data and "greeks" in data
    assert isinstance(data["price"], float)


def test_price_asian_geometric_placeholder():
    payload = {
        "spot": 100, "strike": 100, "rate": 0.01, "div_yield": 0.0,
        "vol": 0.2, "t": 1.0, "average": "geom"
    }
    r = client.post("/api/options/price/asian", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "price" in data or data.get("status") == "not_implemented"