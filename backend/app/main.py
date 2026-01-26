@app.get("/neo4j/consistency-check")
async def neo4j_consistency_check():
    """
    Check if NetworkX graph and Neo4j database are in sync (node/edge counts).
    """
    try:
        nodes_file = os.getenv("NODES_FILE", os.path.join(os.path.dirname(__file__), "usaspending_nodes.json"))
        edges_file = os.getenv("EDGES_FILE", os.path.join(os.path.dirname(__file__), "usaspending_edges.json"))
        G = analytics_engine.build_graph(nodes_path=nodes_file, edges_path=edges_file)
        nx_nodes = G.number_of_nodes()
        nx_edges = G.number_of_edges()
        # Query Neo4j for counts
        node_query = "MATCH (n) RETURN count(n) AS node_count"
        edge_query = "MATCH ()-[r]->() RETURN count(r) AS edge_count"
        neo4j_node_count = neo4j_conn.execute_query(node_query)[0]["node_count"]
        neo4j_edge_count = neo4j_conn.execute_query(edge_query)[0]["edge_count"]
        return {
            "networkx": {"nodes": nx_nodes, "edges": nx_edges},
            "neo4j": {"nodes": neo4j_node_count, "edges": neo4j_edge_count},
            "in_sync": nx_nodes == neo4j_node_count and nx_edges == neo4j_edge_count
        }
    except Exception as e:
        logger.error(f"Neo4j consistency check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Neo4j consistency check error: {str(e)}")
@app.post("/neo4j/refresh")
async def neo4j_refresh():
    """
    Refresh Neo4j database from latest ingested NetworkX graph.
    """
    try:
        nodes_file = os.getenv("NODES_FILE", os.path.join(os.path.dirname(__file__), "usaspending_nodes.json"))
        edges_file = os.getenv("EDGES_FILE", os.path.join(os.path.dirname(__file__), "usaspending_edges.json"))
        G = analytics_engine.build_graph(nodes_path=nodes_file, edges_path=edges_file)
        # Import sync_to_neo4j and run sync
        import sync_to_neo4j
        sync_to_neo4j.sync_graph_to_neo4j(G)
        logger.info("Neo4j database refreshed from NetworkX graph.")
        return {"status": "success", "message": "Neo4j database refreshed from NetworkX graph."}
    except Exception as e:
        logger.error(f"Neo4j refresh error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Neo4j refresh error: {str(e)}")


import os
from dotenv import load_dotenv
import httpx
import logging
# Load environment variables from .env if present
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".env"))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("supply_chain_backend")


# Load environment variables from .env if present
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".env"))

# Finnhub API settings
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "d5qjfahr01qhn30g3dvgd5qjfahr01qhn30g3e00")
FINNHUB_SECRET = os.getenv("FINNHUB_SECRET", "d5qjfahr01qhn30g3e10")
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

def get_finnhub_headers():
    return {
        "X-Finnhub-Secret": FINNHUB_SECRET,
        "Accept": "application/json"
    }

async def finnhub_get(endpoint: str, params: dict = None):
    url = f"{FINNHUB_BASE_URL}/{endpoint}"
    headers = get_finnhub_headers()
    params = params or {}
    params["token"] = FINNHUB_API_KEY
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
import networkx as nx
from neo4j import GraphDatabase
import os

# Import analytics engine
import sys
sys.path.append(os.path.dirname(__file__))
import analytics_engine



# Neo4j connection settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


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


# Pydantic models
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


class ShortestPathRequest(BaseModel):
    network_data: NetworkData
    source: str
    target: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize connections
    neo4j_conn.connect()
    yield
    # Shutdown: Close connections
    neo4j_conn.close()


app = FastAPI(
    title="Supply Chain Network API",
    description="API for supply chain network analytics using NetworkX and Neo4j",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend access
# NOTE: In production, replace ["*"] with specific allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
            "/neo4j/create-sample"
        ]
    }



@app.get("/health")
async def health_check():
    """Health check endpoint"""
    neo4j_status = "connected" if neo4j_conn.driver else "disconnected"
    logger.info(f"Health check requested. Neo4j status: {neo4j_status}")
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
async def shortest_path(request: ShortestPathRequest):
    """
    Find the shortest path between two nodes in the supply chain network
    """
    try:
        # Create NetworkX graph
        G = nx.DiGraph()
        
        for node in request.network_data.nodes:
            G.add_node(node.id, type=node.type, name=node.name)
        
        for edge in request.network_data.edges:
            G.add_edge(edge.source, edge.target, weight=edge.weight)
        
        # Check if nodes exist
        if request.source not in G or request.target not in G:
            raise HTTPException(status_code=404, detail="Source or target node not found")
        
        # Find shortest path
        try:
            path = nx.shortest_path(G, request.source, request.target, weight='weight')
            length = nx.shortest_path_length(G, request.source, request.target, weight='weight')
            
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



# Finnhub Webhook Endpoint (must be after app is defined)
import os
from fastapi import Request

# --- Advanced Analytics Endpoint ---

@app.get("/analytics/metrics")
async def get_advanced_analytics(
    node_type: str = Query(None, description="Filter by node type"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    page_size: int = Query(50, ge=1, le=500, description="Page size for pagination")
):
    """
    Compute and return advanced analytics (degree, eigenvector, authority centrality, risk scores)
    using the ingested USAspending data. Automatically runs ingestion if files are missing.
    """
    import os
    nodes_file = os.getenv("NODES_FILE", os.path.join(os.path.dirname(__file__), "usaspending_nodes.json"))
    edges_file = os.getenv("EDGES_FILE", os.path.join(os.path.dirname(__file__), "usaspending_edges.json"))
    # Check if files exist, run ingestion if missing
    if not (os.path.exists(nodes_file) and os.path.exists(edges_file)):
        try:
            logger.info("Ingested data files missing. Running ingestion script...")
            import subprocess
            result = subprocess.run([
                "python", os.path.join(os.path.dirname(__file__), "ingest_usaspending.py")
            ], capture_output=True, text=True)
            logger.info(f"Ingestion script output: {result.stdout}")
            if result.returncode != 0:
                logger.error(f"Ingestion failed: {result.stderr}")
                raise Exception(f"Ingestion failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Data ingestion error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Data ingestion error: {str(e)}")
    try:
        logger.info("Building graph from ingested data files...")
        G = analytics_engine.build_graph(nodes_path=nodes_file, edges_path=edges_file)
        logger.info(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
        results = analytics_engine.compute_analytics(G)
        logger.info("Analytics computed successfully.")
        # Collect node analytics with all attributes
        node_data = []
        for node in G.nodes:
            if node_type and G.nodes[node].get("type") != node_type:
                continue
            node_info = {
                "id": node,
                "type": G.nodes[node].get("type"),
                "name": G.nodes[node].get("name"),
                "degree_centrality": results["degree_centrality"].get(node, 0),
                "eigenvector_centrality": results["eigenvector_centrality"].get(node, 0),
                "authority": results["authority"].get(node, 0),
                "hub": results["hub"].get(node, 0),
                "risk_score": G.nodes[node].get("risk_score", 0),
                "risk_forecast": G.nodes[node].get("risk_forecast", 0),
                "macro": {
                    "unemployment_rate": G.nodes[node].get("unemployment_rate"),
                    "financial_health": G.nodes[node].get("financial_health"),
                    "location_risk": G.nodes[node].get("location_risk"),
                    "demand_score": G.nodes[node].get("demand_score"),
                }
            }
            node_data.append(node_info)
        # Pagination
        total = len(node_data)
        start = (page - 1) * page_size
        end = start + page_size
        paged_nodes = node_data[start:end]
        # Summary stats
        summary = {
            "total_nodes": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
        return {
            "status": "success",
            "summary": summary,
            "nodes": paged_nodes
        }
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")
@app.post("/webhook/finnhub")
async def finnhub_webhook(request: Request):
    # Acknowledge receipt with 2xx before processing
    # Check secret header
    secret = request.headers.get("x-finnhub-secret")
    if secret != FINNHUB_SECRET:
        # Still return 2xx to avoid disabling endpoint, but log warning
        print("Warning: Invalid Finnhub secret received.")
        return {"status": "ignored", "reason": "invalid secret"}
    # Parse event
    try:
        event = await request.json()
    except Exception:
        event = None
    # Log event for now (replace with business logic as needed)
    print("Received Finnhub event:", event)
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
