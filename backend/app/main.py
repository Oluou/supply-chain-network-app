from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import networkx as nx
from neo4j import GraphDatabase
import os

app = FastAPI(
    title="Supply Chain Network API",
    description="API for supply chain network analytics using NetworkX and Neo4j",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Neo4j connection settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


class Node(BaseModel):
    id: str
    type: str
    name: str
    properties: Optional[Dict] = {}


class Edge(BaseModel):
    source: str
    target: str
    relationship: str
    weight: Optional[float] = 1.0


class NetworkData(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


class Neo4jConnection:
    def __init__(self):
        self.driver = None
    
    def connect(self):
        try:
            self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            return True
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            return False
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def execute_query(self, query, parameters=None):
        if not self.driver:
            self.connect()
        
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]


neo4j_conn = Neo4jConnection()


@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    neo4j_conn.connect()


@app.on_event("shutdown")
async def shutdown_event():
    """Close connections on shutdown"""
    neo4j_conn.close()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Supply Chain Network API",
        "version": "1.0.0",
        "endpoints": [
            "/docs",
            "/network/analyze",
            "/network/shortest-path",
            "/network/centrality",
            "/neo4j/nodes",
            "/neo4j/create-sample"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    neo4j_status = "connected" if neo4j_conn.driver else "disconnected"
    return {
        "status": "healthy",
        "neo4j": neo4j_status
    }


@app.post("/network/analyze")
async def analyze_network(network_data: NetworkData):
    """
    Analyze a supply chain network using NetworkX
    Returns basic network metrics
    """
    try:
        # Create NetworkX graph
        G = nx.DiGraph()
        
        # Add nodes
        for node in network_data.nodes:
            G.add_node(node.id, type=node.type, name=node.name, **node.properties)
        
        # Add edges
        for edge in network_data.edges:
            G.add_edge(edge.source, edge.target, 
                      relationship=edge.relationship, 
                      weight=edge.weight)
        
        # Calculate network metrics
        metrics = {
            "num_nodes": G.number_of_nodes(),
            "num_edges": G.number_of_edges(),
            "density": nx.density(G),
            "is_connected": nx.is_weakly_connected(G),
            "num_components": nx.number_weakly_connected_components(G)
        }
        
        # Calculate degree centrality
        degree_centrality = nx.degree_centrality(G)
        top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        
        metrics["top_central_nodes"] = [
            {"node": node, "centrality": centrality} 
            for node, centrality in top_nodes
        ]
        
        return {
            "status": "success",
            "metrics": metrics
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/network/shortest-path")
async def shortest_path(network_data: NetworkData, source: str, target: str):
    """
    Find the shortest path between two nodes in the supply chain network
    """
    try:
        # Create NetworkX graph
        G = nx.DiGraph()
        
        for node in network_data.nodes:
            G.add_node(node.id, type=node.type, name=node.name)
        
        for edge in network_data.edges:
            G.add_edge(edge.source, edge.target, weight=edge.weight)
        
        # Check if nodes exist
        if source not in G or target not in G:
            raise HTTPException(status_code=404, detail="Source or target node not found")
        
        # Find shortest path
        try:
            path = nx.shortest_path(G, source, target, weight='weight')
            length = nx.shortest_path_length(G, source, target, weight='weight')
            
            return {
                "status": "success",
                "path": path,
                "length": length
            }
        except nx.NetworkXNoPath:
            return {
                "status": "no_path",
                "message": "No path exists between source and target"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/network/centrality")
async def calculate_centrality(network_data: NetworkData):
    """
    Calculate various centrality metrics for supply chain network
    """
    try:
        # Create NetworkX graph
        G = nx.DiGraph()
        
        for node in network_data.nodes:
            G.add_node(node.id, type=node.type, name=node.name)
        
        for edge in network_data.edges:
            G.add_edge(edge.source, edge.target, weight=edge.weight)
        
        # Calculate centrality metrics
        degree_cent = nx.degree_centrality(G)
        betweenness_cent = nx.betweenness_centrality(G)
        
        # Convert to list format
        centrality_data = []
        for node_id in G.nodes():
            centrality_data.append({
                "node_id": node_id,
                "degree_centrality": degree_cent.get(node_id, 0),
                "betweenness_centrality": betweenness_cent.get(node_id, 0)
            })
        
        # Sort by degree centrality
        centrality_data.sort(key=lambda x: x["degree_centrality"], reverse=True)
        
        return {
            "status": "success",
            "centrality_metrics": centrality_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/neo4j/nodes")
async def get_neo4j_nodes():
    """
    Retrieve all nodes from Neo4j database
    """
    try:
        query = "MATCH (n) RETURN n LIMIT 100"
        results = neo4j_conn.execute_query(query)
        return {
            "status": "success",
            "nodes": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j error: {str(e)}")


@app.post("/neo4j/create-sample")
async def create_sample_data():
    """
    Create sample supply chain data in Neo4j
    """
    try:
        # Clear existing data
        neo4j_conn.execute_query("MATCH (n) DETACH DELETE n")
        
        # Create sample nodes
        queries = [
            "CREATE (s:Supplier {id: 'SUP1', name: 'Raw Materials Inc'})",
            "CREATE (m:Manufacturer {id: 'MAN1', name: 'Assembly Corp'})",
            "CREATE (d:Distributor {id: 'DIS1', name: 'Logistics Ltd'})",
            "CREATE (r:Retailer {id: 'RET1', name: 'Retail Store'})",
            "MATCH (s:Supplier {id: 'SUP1'}), (m:Manufacturer {id: 'MAN1'}) CREATE (s)-[:SUPPLIES {weight: 1.0}]->(m)",
            "MATCH (m:Manufacturer {id: 'MAN1'}), (d:Distributor {id: 'DIS1'}) CREATE (m)-[:SHIPS_TO {weight: 1.5}]->(d)",
            "MATCH (d:Distributor {id: 'DIS1'}), (r:Retailer {id: 'RET1'}) CREATE (d)-[:DELIVERS_TO {weight: 2.0}]->(r)"
        ]
        
        for query in queries:
            neo4j_conn.execute_query(query)
        
        return {
            "status": "success",
            "message": "Sample supply chain data created in Neo4j"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
