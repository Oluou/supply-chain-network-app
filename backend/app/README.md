# Supply Chain Network Backend

This backend powers the analytics and data pipeline for the Supply Chain Network App. It provides API endpoints for network analytics, risk computation, and graph persistence using FastAPI, NetworkX, and Neo4j.

## Features
- **API Endpoints**: Expose analytics, network queries, and Neo4j operations via FastAPI.
- **Data Ingestion**: Scripts to extract and normalize entities/relationships from USAspending, SEC EDGAR, OpenCorporates, and Finnhub.
- **Analytics Engine**: Computes degree, eigenvector, authority centrality, and risk scores per GWU thesis methodology.
- **Graph Persistence**: Syncs NetworkX graph to Neo4j for advanced queries and visualization.

## Key Files
- `main.py`: FastAPI app and API endpoints.
- `analytics_engine.py`: Centrality and risk computation logic.
- `build_networkx_graph.py`: Loads nodes/edges and builds NetworkX DiGraph.
- `ingest_usaspending.py`: Ingests and normalizes USAspending data.
- `sync_to_neo4j.py`: Syncs NetworkX graph to Neo4j.

## API Endpoints
See `../docs/apis.md` for full API documentation and example requests/responses.

### Example Endpoints
- `GET /analytics/metrics`: Advanced analytics (degree, eigenvector, authority, risk scores)
- `POST /network/analyze`: Network metrics (density, connectivity, centrality)
- `POST /network/shortest-path`: Shortest path between nodes
- `POST /network/centrality`: Centrality metrics
- `GET /neo4j/nodes`: Retrieve nodes from Neo4j
- `POST /neo4j/create-sample`: Create sample data in Neo4j

## Running the Backend

### Local Development
```bash
cd backend/app
uvicorn main:app --reload
```

### With Docker Compose
```bash
docker-compose up --build
```

## Environment Variables
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: Neo4j connection
- `FINNHUB_API_KEY`, `FINNHUB_SECRET`: Finnhub API credentials

## Testing
- Unit and integration tests are in `tests/`

## Reproducibility
- All scripts and data flows are documented in `../docs/apis.md`.
- Use the provided Dockerfiles and requirements.txt for environment setup.

## References
- See `../docs/apis.md` for architecture, data model mapping, and analytics planning.
