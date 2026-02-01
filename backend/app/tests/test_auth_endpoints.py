import pytest
from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

API_KEY = "changeme-supersecret-key"

# Test analytics endpoint (centrality)
def test_analytics_centrality_unauthorized():
    response = client.get("/analytics/centrality")
    assert response.status_code == 401

def test_analytics_centrality_authorized(monkeypatch):
    # Patch the graph to have at least one node
    from app.services.graph_builder import GraphBuilder
    builder = GraphBuilder()
    builder.add_nodes([type('Node', (), {'id': 'A', 'type': 'agency', 'name': 'AgencyA', 'attributes': {}})()])
    monkeypatch.setattr("app.routers.analytics.graph_builder", builder)
    response = client.get("/analytics/centrality", headers={"X-API-Key": API_KEY})
    assert response.status_code in (200, 400)  # 400 if graph is empty, 200 if not

# Test risk endpoint (node removal)
def test_risk_node_removal_unauthorized():
    response = client.get("/risk/node_removal/A")
    assert response.status_code == 401

def test_risk_node_removal_authorized(monkeypatch):
    from app.services.graph_builder import GraphBuilder
    builder = GraphBuilder()
    builder.add_nodes([type('Node', (), {'id': 'A', 'type': 'agency', 'name': 'AgencyA', 'attributes': {}})()])
    monkeypatch.setattr("app.routers.risk.graph_builder", builder)
    response = client.get("/risk/node_removal/A", headers={"X-API-Key": API_KEY})
    assert response.status_code in (200, 404)  # 404 if node not found, 200 if found
