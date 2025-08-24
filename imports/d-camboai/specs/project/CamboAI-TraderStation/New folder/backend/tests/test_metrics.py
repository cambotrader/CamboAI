import pytest
from httpx import AsyncClient
from app.main import app
from app.core.metrics import MetricsManager

@pytest.mark.asyncio
async def test_metrics_recording():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test request metrics
        response = await client.get("/health")
        assert response.status_code == 200
        
        # Test market data metrics
        MetricsManager.record_market_data_request("AAPL", "1d")
        response = await client.get("/metrics")
        assert "market_data_requests_total" in response.text
        
        # Test analysis metrics
        MetricsManager.record_analysis_request("technical")
        response = await client.get("/metrics")
        assert "analysis_requests_total" in response.text
        
        # Test trading metrics
        MetricsManager.record_trading_order("market", "AAPL", "completed")
        response = await client.get("/metrics")
        assert "trading_orders_total" in response.text

@pytest.mark.asyncio
async def test_error_metrics():
    async with AsyncClient(app=app, base_url="http://test") as client:
        MetricsManager.record_api_error("/api/market-data", "validation_error")
        response = await client.get("/metrics")
        assert "api_errors_total" in response.text

@pytest.mark.asyncio
async def test_cache_metrics():
    async with AsyncClient(app=app, base_url="http://test") as client:
        MetricsManager.record_cache_operation("market_data", True)
        MetricsManager.record_cache_operation("market_data", False)
        response = await client.get("/metrics")
        assert "cache_hits_total" in response.text
        assert "cache_misses_total" in response.text

@pytest.mark.asyncio
async def test_db_metrics():
    async with AsyncClient(app=app, base_url="http://test") as client:
        MetricsManager.update_db_pool_status("active", 5)
        MetricsManager.record_db_query_duration("select", 0.1)
        response = await client.get("/metrics")
        assert "db_connection_pool_size" in response.text
        assert "db_query_duration_seconds" in response.text
