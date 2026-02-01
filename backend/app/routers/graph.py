from fastapi import APIRouter, HTTPException
from app.models.ingestion import NodeModel, EdgeModel
from app.shared_graph import graph_builder
from typing import List

router = APIRouter(prefix="/graph", tags=["graph"])
 

@router.post("/build")
def build_graph(nodes: List[NodeModel], edges: List[EdgeModel]):
    try:
        G = graph_builder.build_from_data(nodes, edges)
        return {"message": "Graph built successfully", "num_nodes": G.number_of_nodes(), "num_edges": G.number_of_edges()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update")
def update_graph(nodes: List[NodeModel] = [], edges: List[EdgeModel] = []):
    try:
        G = graph_builder.update_graph(nodes, edges)
        return {"message": "Graph updated successfully", "num_nodes": G.number_of_nodes(), "num_edges": G.number_of_edges()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
