from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_api_key
from app.utils.logging import get_logger

logger = get_logger("analytics")

from app.shared_graph import graph_builder
import networkx as nx
from typing import Dict, Any

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/centrality")
def get_centrality(api_key: str = Depends(get_api_key)):
    G = graph_builder.to_networkx()
    if G.number_of_nodes() == 0:
        logger.warning("Centrality requested on empty graph")
        raise HTTPException(status_code=400, detail="Graph is empty")
    try:
        degree = nx.degree_centrality(G)
        eigen = nx.eigenvector_centrality(G, max_iter=1000)
        betweenness = nx.betweenness_centrality(G)
        result = {
            "degree_centrality": degree,
            "eigenvector_centrality": eigen,
            "betweenness_centrality": betweenness
        }
        logger.info("Centrality computed successfully")
        return result
    except Exception as e:
        logger.error(f"Centrality computation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/node_metrics/{node_id}")
def get_node_metrics(node_id: str, api_key: str = Depends(get_api_key)) -> Dict[str, Any]:
    G = graph_builder.to_networkx()
    if node_id not in G:
        logger.warning(f"Node metrics requested for missing node: {node_id}")
        raise HTTPException(status_code=404, detail="Node not found")
    return {
        "degree": G.degree(node_id),
        "in_degree": G.in_degree(node_id),
        "out_degree": G.out_degree(node_id),
        "neighbors": list(G.neighbors(node_id))
    }
