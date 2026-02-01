from fastapi import APIRouter, Query
from app.services.graph_builder import GraphBuilder
from typing import List, Dict, Any

router = APIRouter(prefix="/edges", tags=["edges"])

graph_builder = GraphBuilder()

@router.get("/")
def list_edges(skip: int = Query(0, ge=0), limit: int = Query(100, le=1000)) -> Dict[str, Any]:
    G = graph_builder.to_networkx()
    edges = list(G.edges(data=True))
    paginated = edges[skip:skip+limit]
    return {
        "total": len(edges),
        "skip": skip,
        "limit": limit,
        "edges": [{"source": u, "target": v, **attrs} for u, v, attrs in paginated]
    }

@router.get("/{source}/{target}")
def get_edge(source: str, target: str) -> Dict[str, Any]:
    G = graph_builder.to_networkx()
    if not G.has_edge(source, target):
        return {"error": "Edge not found"}
    return {"source": source, "target": target, **G.edges[source, target]}
