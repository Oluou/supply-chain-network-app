import networkx as nx
from app.models.ingestion import NodeModel, EdgeModel
from typing import List, Optional

class GraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_nodes(self, nodes: List[NodeModel]):
        for node in nodes:
            self.graph.add_node(node.id, **(node.attributes or {}), type=node.type, name=node.name)

    def add_edges(self, edges: List[EdgeModel]):
        for edge in edges:
            self.graph.add_edge(edge.source, edge.target, **(edge.attributes or {}), value=edge.value)

    def build_from_data(self, nodes: List[NodeModel], edges: List[EdgeModel]):
        self.add_nodes(nodes)
        self.add_edges(edges)
        return self.graph

    def update_graph(self, nodes: Optional[List[NodeModel]] = None, edges: Optional[List[EdgeModel]] = None):
        if nodes:
            self.add_nodes(nodes)
        if edges:
            self.add_edges(edges)
        return self.graph

    def to_networkx(self):
        return self.graph
