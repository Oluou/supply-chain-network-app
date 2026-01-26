
import sys, os
import pytest
import networkx as nx
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
import analytics_engine

def test_build_graph_valid():
    nodes = [
        {"id": "A", "type": "Supplier", "name": "Alpha"},
        {"id": "B", "type": "Prime", "name": "Beta"}
    ]
    edges = [
        {"source": "A", "target": "B", "relationship": "SUPPLIES", "weight": 1.0}
    ]
    import json, tempfile, os
    with tempfile.TemporaryDirectory() as tmp:
        nodes_path = os.path.join(tmp, "nodes.json")
        edges_path = os.path.join(tmp, "edges.json")
        with open(nodes_path, "w") as f: json.dump(nodes, f)
        with open(edges_path, "w") as f: json.dump(edges, f)
        G = analytics_engine.build_graph(nodes_path, edges_path)
        assert G.number_of_nodes() == 2
        assert G.number_of_edges() == 1
        assert "A" in G.nodes and "B" in G.nodes
        assert G.has_edge("A", "B")

def test_build_graph_invalid_node():
    nodes = [{"type": "Supplier", "name": "Alpha"}]  # missing id
    edges = []
    import json, tempfile, os
    with tempfile.TemporaryDirectory() as tmp:
        nodes_path = os.path.join(tmp, "nodes.json")
        edges_path = os.path.join(tmp, "edges.json")
        with open(nodes_path, "w") as f: json.dump(nodes, f)
        with open(edges_path, "w") as f: json.dump(edges, f)
        with pytest.raises(ValueError):
            analytics_engine.build_graph(nodes_path, edges_path)

def test_build_graph_invalid_edge():
    nodes = [{"id": "A", "type": "Supplier", "name": "Alpha"}]
    edges = [{"target": "A"}]  # missing source
    import json, tempfile, os
    with tempfile.TemporaryDirectory() as tmp:
        nodes_path = os.path.join(tmp, "nodes.json")
        edges_path = os.path.join(tmp, "edges.json")
        with open(nodes_path, "w") as f: json.dump(nodes, f)
        with open(edges_path, "w") as f: json.dump(edges, f)
        with pytest.raises(ValueError):
            analytics_engine.build_graph(nodes_path, edges_path)

def test_compute_analytics():
    G = nx.DiGraph()
    G.add_node("A", type="Supplier", name="Alpha")
    G.add_node("B", type="Prime", name="Beta")
    G.add_edge("A", "B", relationship="SUPPLIES", weight=1.0)
    results = analytics_engine.compute_analytics(G)
    assert "degree_centrality" in results
    assert "eigenvector_centrality" in results
    assert "authority" in results
    assert "hub" in results
    assert "A" in G.nodes and "risk_score" in G.nodes["A"]
