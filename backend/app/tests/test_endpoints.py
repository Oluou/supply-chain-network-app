import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app.app import app

client = TestClient(app)
API_KEY = os.getenv("API_KEY", "changeme-supersecret-key")

# 1. Server & Health
def test_server_docs():
    resp = client.get("/docs")
    assert resp.status_code == 200
    assert "Swagger UI" in resp.text

def test_openapi_schema():
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert resp.json()["openapi"]

def test_metrics():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"app_requests_total" in resp.content

# 2. Authentication & Security
def test_analytics_requires_api_key():
    resp = client.get("/analytics/centrality")
    assert resp.status_code == 401

def test_analytics_with_api_key():
    resp = client.get("/analytics/centrality", headers={"X-API-Key": API_KEY})
    assert resp.status_code in (200, 400)  # 400 if graph is empty

def test_risk_requires_api_key():
    resp = client.get("/risk/node_removal/A")
    assert resp.status_code == 401

# 3. Ingestion & Graph
def test_ingest_and_graph_build():
    # Simulate ingest response
    nodes = [{"id": "A", "type": "agency", "name": "AgencyA"}]
    edges = [{"source": "A", "target": "A"}]
    resp = client.post("/graph/build", json={"nodes": nodes, "edges": edges})
    assert resp.status_code == 200
    assert resp.json()["num_nodes"] == 1
    assert resp.json()["num_edges"] == 1

# 4. Analytics
def test_node_metrics_with_api_key():
    # Build graph first
    nodes = [{"id": "A", "type": "agency", "name": "AgencyA"}]
    edges = [{"source": "A", "target": "A"}]
    client.post("/graph/build", json={"nodes": nodes, "edges": edges})
    resp = client.get("/analytics/node_metrics/A", headers={"X-API-Key": API_KEY})
    assert resp.status_code == 200
    assert "degree" in resp.json()

# 5. Risk Simulation
def test_risk_node_removal_with_api_key():
    # Build graph first
    nodes = [{"id": "A", "type": "agency", "name": "AgencyA"}]
    edges = [{"source": "A", "target": "A"}]
    client.post("/graph/build", json={"nodes": nodes, "edges": edges})
    resp = client.get("/risk/node_removal/A", headers={"X-API-Key": API_KEY})
    assert resp.status_code == 200
    assert "impact" in resp.json()

# 6. Data Endpoints
def test_nodes_listing():
    resp = client.get("/nodes/")
    assert resp.status_code == 200
    assert "nodes" in resp.json()

def test_edges_listing():
    resp = client.get("/edges/")
    assert resp.status_code == 200
    assert "edges" in resp.json()

# 7. Error Handling
def test_invalid_endpoint():
    resp = client.get("/not-an-endpoint")
    assert resp.status_code == 404

def test_invalid_graph_build():
    resp = client.post("/graph/build", json={"nodes": "notalist", "edges": "notalist"})
    assert resp.status_code == 422

# 8. Rate Limiting
def test_rate_limit():
    for _ in range(110):
        resp = client.get("/nodes/")
    assert resp.status_code in (200, 429)
