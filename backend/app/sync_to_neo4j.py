"""
Sync NetworkX Graph to Neo4j
Loads nodes and edges from JSON and writes them to Neo4j for persistence and advanced queries.
"""
import json
import networkx as nx
from neo4j import GraphDatabase

NODES_FILE = "usaspending_nodes.json"
EDGES_FILE = "usaspending_edges.json"

NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"


def build_graph(nodes_path=NODES_FILE, edges_path=EDGES_FILE):
    G = nx.DiGraph()
    with open(nodes_path) as f:
        nodes = json.load(f)
        for node in nodes:
            node_id = node.pop("id")
            G.add_node(node_id, **node)
    with open(edges_path) as f:
        edges = json.load(f)
        for edge in edges:
            src = edge.pop("source")
            tgt = edge.pop("target")
            G.add_edge(src, tgt, **edge)
    return G

def sync_to_neo4j(G):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        # Create nodes
        for node, attrs in G.nodes(data=True):
            label = attrs.get("type", "Entity")
            props = {k: v for k, v in attrs.items() if v is not None}
            props_str = ", ".join(f"{k}: ${k}" for k in props)
            cypher = f"MERGE (n:{label} {{id: $id}}) SET n += {{{props_str}}}"
            session.run(cypher, id=node, **props)
        # Create edges
        for src, tgt, attrs in G.edges(data=True):
            rel = attrs.get("type", "CONNECTED")
            props = {k: v for k, v in attrs.items() if v is not None and k != "type"}
            props_str = ", ".join(f"r.{k} = ${k}" for k in props)
            cypher = f"MATCH (a {{id: $src}}), (b {{id: $tgt}}) MERGE (a)-[r:{rel}]->(b)"
            if props:
                cypher += f" SET {props_str}"
            session.run(cypher, src=src, tgt=tgt, **props)
    driver.close()

if __name__ == "__main__":
    G = build_graph()
    sync_to_neo4j(G)
    print(f"Synced {G.number_of_nodes()} nodes and {G.number_of_edges()} edges to Neo4j.")
