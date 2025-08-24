import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_portfolio_summary_v1():
    r = client.get("/api/v1/portfolio/summary")
    assert r.status_code == 200
    body = r.json()
    assert "positions" in body and isinstance(body["positions"], list)
    assert "total_value" in body