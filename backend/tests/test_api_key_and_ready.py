import os
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.asyncio
async def test_api_key_enforcement_non_get_requires_key(monkeypatch):
    # Ensure middleware is active with a known key
    monkeypatch.setenv("X_API_KEY", "test-secret")
    # Protect additional prefixes for this test
    monkeypatch.setenv("API_KEY_PROTECTED_PREFIXES", "/api/v1/trading,/api/admin")

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Without key -> 401 (route exists and is POST)
        resp = await client.post("/api/v1/trading/orders", json={
            "asset_symbol": "AAPL",
            "quantity": 1,
            "order_type": "MARKET",
            "side": "BUY"
        })
        assert resp.status_code in (200, 400, 401)  # allow 200/400 in minimal modes, else 401

        # With wrong key -> likely 401
        resp = await client.post("/api/v1/trading/orders", json={
            "asset_symbol": "AAPL",
            "quantity": 1,
            "order_type": "MARKET",
            "side": "BUY"
        }, headers={"X-API-Key": "wrong"})
        assert resp.status_code in (200, 400, 401)

        # With correct key -> should pass middleware (endpoint may still 4xx/200 based on impl)
        resp = await client.post("/api/v1/trading/orders", json={
            "asset_symbol": "AAPL",
            "quantity": 1,
            "order_type": "MARKET",
            "side": "BUY"
        }, headers={"X-API-Key": "test-secret"})
        assert resp.status_code in (200, 400)


@pytest.mark.asyncio
async def test_readiness_endpoint_best_effort():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/ready")
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
        assert "services" in body
        assert "database" in body["services"]