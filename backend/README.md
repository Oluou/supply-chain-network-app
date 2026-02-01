# Supply Chain Network Analytics API - Deployment & Usage

## Overview
This backend provides RESTful endpoints for ingesting, analyzing, and simulating supply chain network data. It is built with FastAPI, NetworkX, and Neo4j, and is fully containerized for local and cloud deployment.

---

## Deployment

### Prerequisites
- Docker & Docker Compose
- (Optional) Prometheus for monitoring

### Quick Start
1. Clone the repository.
2. Set environment variables in `.env` or via your deployment platform (see docker-compose.yml for required variables).
3. Build and start the stack:
   ```sh
   docker-compose up --build
   ```
4. Access the API docs at: http://localhost:8000/docs
5. Prometheus metrics available at: http://localhost:8000/metrics

---

## API Authentication
- All analytics and risk endpoints require an API key via the `X-API-Key` header.
- Default key: `changeme-supersecret-key` (change in production!)

---

## Key Endpoints

- **/ingest/**: Ingest data from external sources (usaspending, edgar, finnhub, wikidata)
- **/graph/build**: Build a directed graph from nodes/edges
- **/neo4j/persist**: Persist the current graph to Neo4j
- **/analytics/centrality**: Get centrality metrics (API key required)
- **/analytics/node_metrics/{node_id}**: Get node metrics (API key required)
- **/risk/node_removal/{node_id}**: Simulate node removal (API key required)
- **/nodes/**: List nodes (paginated)
- **/edges/**: List edges (paginated)
- **/metrics**: Prometheus metrics for monitoring

---

## Testing
- Run tests with pytest:
  ```sh
  docker-compose run backend pytest
  ```

---

## Monitoring
- Prometheus metrics are exposed at `/metrics`.
- Integrate with Prometheus and Grafana for dashboards.

---

## Security
- Change all default secrets and API keys before production.
- Use HTTPS in production deployments.

---

## Contributing
- See CONTRIBUTING.md (if available) for guidelines.

---

## License
- See LICENSE file.
