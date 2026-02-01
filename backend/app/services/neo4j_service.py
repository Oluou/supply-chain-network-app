from neo4j import GraphDatabase
import os
from app.models.ingestion import NodeModel, EdgeModel
from typing import List

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class Neo4jService:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def persist_graph(self, nodes: List[NodeModel], edges: List[EdgeModel]):
        with self.driver.session() as session:
            # Batch create nodes
            for node in nodes:
                session.execute_write(self._create_node, node)
            # Batch create edges
            for edge in edges:
                session.execute_write(self._create_edge, edge)

    @staticmethod
    def _create_node(tx, node: NodeModel):
        tx.run(
            """
            MERGE (n:Entity {id: $id})
            SET n.type = $type, n.name = $name, n += $attributes
            """,
            id=node.id, type=node.type, name=node.name, attributes=node.attributes or {}
        )

    @staticmethod
    def _create_edge(tx, edge: EdgeModel):
        tx.run(
            """
            MATCH (src:Entity {id: $source}), (tgt:Entity {id: $target})
            MERGE (src)-[r:CONTRACT {value: $value}]->(tgt)
            SET r += $attributes
            """,
            source=edge.source, target=edge.target, value=edge.value, attributes=edge.attributes or {}
        )
