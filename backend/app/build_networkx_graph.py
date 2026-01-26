"""
NetworkX Graph Builder for Industrial Network
Loads nodes and edges from JSON (output of ingest_usaspending.py) and builds a directed graph.
"""
import json
import networkx as nx

NODES_FILE = "usaspending_nodes.json"
EDGES_FILE = "usaspending_edges.json"


def build_graph(nodes_path=NODES_FILE, edges_path=EDGES_FILE):
    G = nx.DiGraph()
    # Load nodes
    with open(nodes_path) as f:
        nodes = json.load(f)
        for node in nodes:
            node_id = node.pop("id")
            G.add_node(node_id, **node)
    # Load edges
    with open(edges_path) as f:
        edges = json.load(f)
        for edge in edges:
            src = edge.pop("source")
            tgt = edge.pop("target")
            G.add_edge(src, tgt, **edge)
    return G

if __name__ == "__main__":
    G = build_graph()
    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    # Example: print top 5 nodes by degree centrality
    dc = nx.degree_centrality(G)
    top = sorted(dc.items(), key=lambda x: x[1], reverse=True)[:5]
    print("Top nodes by degree centrality:")
    for node, score in top:
        print(f"{node}: {score:.3f}")
