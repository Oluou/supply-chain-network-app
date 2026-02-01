import pytest
from fastapi.testclient import TestClient
from app.app import app
import os

client = TestClient(app)
API_KEY = os.getenv("API_KEY", "changeme-supersecret-key")

# Test CORS headers
def test_cors_headers():
    resp = client.options(
        "/nodes/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert resp.status_code in (200, 204)
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"

# Test logging and error handling
def test_internal_server_error(monkeypatch):
    # Patch a route to raise an error
    from app.routers.analytics import get_centrality
    monkeypatch.setattr("app.routers.analytics.get_centrality", lambda *a, **kw: 1/0)
    resp = client.get("/analytics/centrality", headers={"X-API-Key": API_KEY})
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Internal server error"
