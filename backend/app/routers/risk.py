from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_api_key
from app.utils.logging import get_logger

logger = get_logger("risk")
import networkx as nx
from typing import Dict, Any

router = APIRouter(prefix="/risk", tags=["risk"])

from app.shared_graph import graph_builder

@router.get("/node_removal/{node_id}")
def node_removal_impact(node_id: str, api_key: str = Depends(get_api_key)) -> Dict[str, Any]:
    G = graph_builder.to_networkx()
    if node_id not in G:
        logger.warning(f"Risk analysis requested for missing node: {node_id}")
        raise HTTPException(status_code=404, detail="Node not found")
    try:
        # Compute original metrics
        original_components = nx.number_weakly_connected_components(G)
        original_size = G.number_of_nodes()
        # Remove node and recompute
        G_removed = G.copy()
        G_removed.remove_node(node_id)
        new_components = nx.number_weakly_connected_components(G_removed)
        new_size = G_removed.number_of_nodes()
        # Optionally, recalculate centrality or other metrics
        result = {
            "original_num_nodes": original_size,
            "new_num_nodes": new_size,
            "original_components": original_components,
            "new_components": new_components,
            "nodes_removed": [node_id],
            "impact": {
                "component_change": new_components - original_components,
                "size_change": new_size - original_size
            }
        }
        logger.info(f"Risk analysis for node {node_id} completed")
        return result
    except Exception as e:
        logger.error(f"Risk analysis failed for node {node_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
