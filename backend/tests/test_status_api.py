import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_status_v1():
    r = client.get("/api/v1/status")
    assert r.status_code == 200
    body = r.json()
    assert body.get("name")
    assert body.get("services", {}).get("api") == "online"