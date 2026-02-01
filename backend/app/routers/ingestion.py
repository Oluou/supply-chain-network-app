from app.models.ingestion import IngestionRequest, IngestionResponse, NodeModel, EdgeModel
from app.services.usaspending_service import USASpendingService
from app.services.edgar_service import EdgarService
from app.services.finnhub_service import FinnhubService
from app.services.wikidata_service import WikidataService
from fastapi import APIRouter, HTTPException
from typing import Any

router = APIRouter(prefix="/ingest", tags=["ingestion"])

@router.post("/", response_model=IngestionResponse)
async def ingest_data(request: IngestionRequest) -> IngestionResponse:
    if request.source == "usaspending":
        service = USASpendingService()
        contracts = service.get_contracts(**request.params)
        # Transform contracts to NodeModel/EdgeModel lists (pseudo-code)
        nodes, edges = [], []
        # ... populate nodes, edges ...
        return IngestionResponse(nodes=nodes, edges=edges)
    elif request.source == "edgar":
        service = EdgarService()
        filings = service.get_filings(**request.params)
        nodes, edges = [], []
        # ... populate nodes, edges ...
        return IngestionResponse(nodes=nodes, edges=edges)
    elif request.source == "finnhub":
        service = FinnhubService()
        profile = await service.get_company_profile(**request.params)
        nodes, edges = [], []
        # ... populate nodes, edges ...
        return IngestionResponse(nodes=nodes, edges=edges)
    elif request.source == "wikidata":
        service = WikidataService()
        data = await service.query(request.params.get("sparql_query", ""))
        nodes, edges = [], []
        # ... populate nodes, edges ...
        return IngestionResponse(nodes=nodes, edges=edges)
    else:
        raise HTTPException(status_code=400, detail="Unknown data source")
