from pydantic import BaseModel
from typing import List, Optional

class NodeModel(BaseModel):
    id: str
    type: str
    name: str
    attributes: Optional[dict] = None

class EdgeModel(BaseModel):
    source: str
    target: str
    value: Optional[float] = None
    attributes: Optional[dict] = None

class IngestionRequest(BaseModel):
    source: str  # e.g., 'usaspending', 'edgar', 'finnhub', 'wikidata'
    params: dict

class IngestionResponse(BaseModel):
    nodes: List[NodeModel]
    edges: List[EdgeModel]
