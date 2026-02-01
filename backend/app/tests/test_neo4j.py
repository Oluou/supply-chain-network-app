import pytest
from fastapi.testclient import TestClient
from app.app import app
import os

client = TestClient(app)
API_KEY = os.getenv("API_KEY", "changeme-supersecret-key")

# Neo4j integration test (requires running Neo4j container)
def test_neo4j_persist_and_query():
    nodes = [
        {"id": "A", "type": "agency", "name": "AgencyA"},
        {"id": "B", "type": "company", "name": "CompanyB"}
    ]
    edges = [
        {"source": "A", "target": "B", "value": 100.0}
    ]
    # Persist graph
    resp = client.post("/neo4j/persist", json={"nodes": nodes, "edges": edges})
    assert resp.status_code == 200
    # (Optional) Query Neo4j directly if testcontainers or a test DB is available
    # Here, just check the response
    assert "successfully" in resp.json()["message"]
