from fastapi import APIRouter, HTTPException
import logging
from app.models.ingestion import NodeModel, EdgeModel
from app.services.neo4j_service import Neo4jService
from typing import List

router = APIRouter(prefix="/neo4j", tags=["neo4j"])

@router.post("/persist")
def persist_graph(nodes: List[NodeModel], edges: List[EdgeModel]):
    service = Neo4jService()
    try:
        service.persist_graph(nodes, edges)
        return {"message": "Graph persisted to Neo4j successfully"}
    except Exception as e:
        logging.error(f"Neo4j persist error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()
