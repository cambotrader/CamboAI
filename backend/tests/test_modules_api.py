import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_pattern_scan_stub():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post("/api/patterns/scan", json={"symbol": "AAPL", "timeframe": "1D"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["symbol"] == "AAPL"
        assert isinstance(data.get("detections"), list)
        assert len(data["detections"]) >= 1

@pytest.mark.asyncio
async def test_news_headlines_stub():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/api/news/headlines?symbol=AAPL")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data and isinstance(data["items"], list)

@pytest.mark.asyncio
async def test_progress_logs_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/api/progress/logs")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data