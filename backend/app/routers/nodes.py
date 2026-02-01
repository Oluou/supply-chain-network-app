from fastapi import APIRouter, Query
from app.services.graph_builder import GraphBuilder
from typing import List, Dict, Any

router = APIRouter(prefix="/nodes", tags=["nodes"])

graph_builder = GraphBuilder()

@router.get("/")
def list_nodes(skip: int = Query(0, ge=0), limit: int = Query(100, le=1000)) -> Dict[str, Any]:
    G = graph_builder.to_networkx()
    nodes = list(G.nodes(data=True))
    paginated = nodes[skip:skip+limit]
    return {
        "total": len(nodes),
        "skip": skip,
        "limit": limit,
        "nodes": [{"id": n, **attrs} for n, attrs in paginated]
    }

@router.get("/{node_id}")
def get_node(node_id: str) -> Dict[str, Any]:
    G = graph_builder.to_networkx()
    if node_id not in G:
        return {"error": "Node not found"}
    return {"id": node_id, **G.nodes[node_id]}
