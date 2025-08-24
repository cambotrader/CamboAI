from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_sentiment_v2_aggregate():
    docs = [
        {"id": "1", "source": "demo", "title": "Apple beats earnings expectations", "text": "Strong iPhone sales"},
        {"id": "2", "source": "demo", "title": "Fed signals pause", "text": "Rates stable"},
    ]
    r = client.post("/api/v2/sentiment/aggregate", json=docs)
    assert r.status_code == 200
    body = r.json()
    assert "score" in body and "label" in body