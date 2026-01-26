"""
Analytics Engine: Centrality and Systemic Risk Computation
Loads a directed graph and computes degree, eigenvector, and authority centrality,
then quantifies systemic risk per GWU thesis methodology.
"""
import json
import networkx as nx
import numpy as np

NODES_FILE = "usaspending_nodes.json"
EDGES_FILE = "usaspending_edges.json"


def build_graph(nodes_path=NODES_FILE, edges_path=EDGES_FILE):
    G = nx.DiGraph()
    # Validate nodes file
    with open(nodes_path) as f:
        nodes = json.load(f)
        for node in nodes:
            if "id" not in node or "type" not in node or "name" not in node:
                raise ValueError(f"Node missing required fields: {node}")
            node_id = node.pop("id")
            G.add_node(node_id, **node)
    # Validate edges file
    with open(edges_path) as f:
        edges = json.load(f)
        for edge in edges:
            if "source" not in edge or "target" not in edge:
                raise ValueError(f"Edge missing required fields: {edge}")
            src = edge.pop("source")
            tgt = edge.pop("target")
            G.add_edge(src, tgt, **edge)
    return G

def compute_analytics(G):
    results = {}
    # Degree centrality
    results["degree_centrality"] = nx.degree_centrality(G)
    # Eigenvector centrality (for directed, use G.reverse() if needed)
    try:
        results["eigenvector_centrality"] = nx.eigenvector_centrality_numpy(G)
    except Exception:
        results["eigenvector_centrality"] = {}
    # Authority centrality (HITS algorithm)
    try:
        hits = nx.hits_numpy(G)
        results["authority"] = hits[1]
        results["hub"] = hits[0]
    except Exception:
        results["authority"] = {}
        results["hub"] = {}

        # Macro risk schema: overlay macroeconomic attributes
        # Example attributes: unemployment_rate, financial_health, location_risk, demand_score
        for node in G.nodes:
            # Placeholder: in real use, these would be loaded from external data sources
            G.nodes[node]["unemployment_rate"] = 0.05  # Example static value
            G.nodes[node]["financial_health"] = 0.8    # Example static value
            G.nodes[node]["location_risk"] = 0.2       # Example static value
            G.nodes[node]["demand_score"] = 0.7        # Example static value

        # Risk forecasting prototype: combine centrality and macro attributes
        for node in G.nodes:
            deg = results["degree_centrality"].get(node, 0)
            eig = results["eigenvector_centrality"].get(node, 0)
            auth = results["authority"].get(node, 0)
            # Simple weighted sum for demonstration
            macro = (
                0.2 * G.nodes[node]["unemployment_rate"] +
                0.3 * G.nodes[node]["financial_health"] +
                0.2 * G.nodes[node]["location_risk"] +
                0.3 * G.nodes[node]["demand_score"]
            )
            G.nodes[node]["risk_score"] = float(deg + eig + auth + macro)
            G.nodes[node]["risk_forecast"] = float(G.nodes[node]["risk_score"] * 1.05)  # Example: forecast = risk_score * 1.05
        return results

if __name__ == "__main__":
    G = build_graph()
    analytics = compute_analytics(G)
    # Print top 5 nodes by risk score
    top = sorted(G.nodes(data=True), key=lambda x: x[1].get("risk_score", 0), reverse=True)[:5]
    print("Top nodes by risk score:")
    for node, data in top:
        print(f"{node}: {data.get('risk_score', 0):.3f}")
    # Optionally, save analytics to file
    with open("analytics_results.json", "w") as f:
        json.dump(analytics, f, indent=2)
