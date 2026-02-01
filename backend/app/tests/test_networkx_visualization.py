
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import matplotlib.pyplot as plt
import networkx as nx
from app.services.graph_builder import GraphBuilder
from app.models.ingestion import NodeModel, EdgeModel

# Create nodes and edges
nodes = [
    NodeModel(id="A", type="agency", name="AgencyA"),
    NodeModel(id="B", type="company", name="CompanyB"),
    NodeModel(id="C", type="supplier", name="SupplierC")
]
edges = [
    EdgeModel(source="A", target="B", value=100.0),
    EdgeModel(source="B", target="C", value=50.0),
    EdgeModel(source="C", target="A", value=25.0)
]

# Build the graph
graph_builder = GraphBuilder()
graph_builder.build_from_data(nodes, edges)
G = graph_builder.to_networkx()

# Draw the graph
pos = nx.spring_layout(G)
labels = {n: G.nodes[n]['name'] for n in G.nodes}
edge_labels = {(u, v): d['value'] for u, v, d in G.edges(data=True)}

plt.figure(figsize=(6, 4))
nx.draw(G, pos, with_labels=True, labels=labels, node_color='skyblue', node_size=1200, font_size=10, font_weight='bold', arrows=True)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
plt.title("Supply Chain Network Example")
plt.tight_layout()
plt.show()
