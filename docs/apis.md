# Supply Chain Network App API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
	- [GET /items](#get-items)
	- [POST /items](#post-items)
	- [PUT /items/{id}](#put-itemsid)
	- [DELETE /items/{id}](#delete-itemsid)
4. [Error Handling](#error-handling)
5. [Examples](#examples)
6. [Contact](#contact)
7. [Analytics Engine Planning](#analytics-engine-planning)

---

## Overview


## Authentication

### Finnhub API

- **API Key:** Stored as environment variable `FINNHUB_API_KEY` (default: `d5qjfahr01qhn30g3dvgd5qjfahr01qhn30g3e00`).
- **Secret:** Stored as environment variable `FINNHUB_SECRET` (default: `d5qjfahr01qhn30g3e10`).
- **Header:** All requests to Finnhub from the backend include `X-Finnhub-Secret: <secret>`.

Example request header:

```http
X-Finnhub-Secret: d5qjfahr01qhn30g3e10
```

### Webhook Security

- The webhook endpoint `/webhook/finnhub` expects the header `X-Finnhub-Secret` to match the configured secret.
- If the secret is invalid, the event is ignored but a 2xx status is still returned to avoid endpoint disablement.


## Endpoints

### POST /webhook/finnhub

Receives event notifications from Finnhub. Always returns 2xx status to acknowledge receipt before processing logic.

**Headers:**
- `X-Finnhub-Secret: <secret>`

**Request Body:**
- JSON event payload from Finnhub

**Response:**
- `{ "status": "ok" }` if accepted
- `{ "status": "ignored", "reason": "invalid secret" }` if secret is invalid

### GET /items

### POST /items

### PUT /items/{id}

### DELETE /items/{id}

## Expanded API Endpoints

### Network Analytics

#### POST /network/analyze
Analyze supply chain network metrics (density, centrality, components).

**Request Body:**
```json
{
  "nodes": [
    {"id": "SUP1", "type": "Supplier", "name": "Raw Materials Inc"},
    {"id": "MAN1", "type": "Manufacturer", "name": "Assembly Corp"},
    {"id": "DIS1", "type": "Distributor", "name": "Logistics Ltd"}
  ],
  "edges": [
    {"source": "SUP1", "target": "MAN1", "relationship": "SUPPLIES", "weight": 1.0},
    {"source": "MAN1", "target": "DIS1", "relationship": "SHIPS_TO", "weight": 1.5}
  ]
}
```
**Response:**
```json
{
  "num_nodes": 3,
  "num_edges": 2,
  "density": 0.333,
  "is_connected": true,
  "num_components": 1,
  "degree_centrality": {"SUP1": 0.5, "MAN1": 1.0, "DIS1": 0.5}
}
```

#### POST /network/shortest-path
Find the shortest path between two nodes.

**Request Body:**
```json
{
  "network_data": { ... },
  "source": "SUP1",
  "target": "DIS1"
}
```
**Response:**
```json
{
  "status": "success",
  "path": ["SUP1", "MAN1", "DIS1"],
  "length": 2.5
}
```

#### POST /network/centrality
Calculate centrality metrics for the network.

**Request Body:**
Same as /network/analyze

**Response:**
```json
{
  "status": "success",
  "centrality_metrics": [
    {"id": "MAN1", "degree_centrality": 1.0, "eigenvector_centrality": 0.7, "authority": 0.6},
    ...
  ]
}
```


### Advanced Analytics


#### GET /analytics/metrics
Returns paginated, filterable analytics for nodes in the supply chain network, including centrality, macro risk, and forecast scores.

**Query Parameters:**
- `node_type` (optional): Filter nodes by type (e.g., `prime_contractor`, `supplier`, etc.)
- `page` (default: 1): Page number for pagination
- `page_size` (default: 50): Number of nodes per page (max: 500)

**Response:**
```json
{
  "status": "success",
  "summary": {
    "total_nodes": 1989,
    "page": 1,
    "page_size": 50,
    "total_pages": 40
  },
  "nodes": [
    {
      "id": "prime:039267141",
      "type": "prime_contractor",
      "name": "Raytheon Company",
      "degree_centrality": 0.259,
      "eigenvector_centrality": 0.71,
      "authority": 0.88,
      "hub": 0.78,
      "risk_score": 2.59,
      "risk_forecast": 2.72,
      "macro": {
        "unemployment_rate": 0.05,
        "financial_health": 0.8,
        "location_risk": 0.2,
        "demand_score": 0.7
      }
    },
    // ... more nodes
  ]
}
```

**Frontend Integration Tips:**
- Use `summary` for pagination controls.
- Filter nodes by `type` for targeted views (e.g., only suppliers).
- Display centrality and risk metrics in tables, charts, or network visualizations.
- Macro attributes can be used for advanced filtering or risk overlays.

**Example Usage:**
- `/analytics/metrics?page=2&page_size=100&node_type=supplier`

**Best Practices:**
- Always paginate large requests for performance.
- Use filtering to reduce payload size and improve UX.

### Neo4j Operations

#### GET /neo4j/nodes
Get all nodes from the Neo4j database.

**Response:**
```json
[
  {"id": "SUP1", "type": "Supplier", "name": "Raw Materials Inc"},
  ...
]
```

#### POST /neo4j/create-sample
Create sample supply chain data in Neo4j.

**Response:**
```json
{
  "status": "success",
  "message": "Sample supply chain data created in Neo4j"
}
```

## Error Handling

## Examples

## Contact

## Criteria
- OpenCorporates: Gives company details and corporate groupings/ownership as edges (e.g., controlling entities).
- Finnhub: Supplies direct supplier/customer links for stock-tickered companies, forming supply chain edges with correlation scores for risk weighting.
- SEC EDGAR: Filings like 10-K contain subsidiary lists (often in Exhibit 21), which you parse as edges from parent to child companies.
- USA Spending: Contract awards link recipients (suppliers) to agencies, creating edges for government-related risks (e.g., dependency on federal contracts).

## API 1: [API Name]
- Description: ...
- Sign-up: ...
- Key Endpoints: ...
- Sample Request/Response: ...
- Integration Notes: For our app, use to populate Neo4j graphs.


## Analytics Engine & Reproducibility

The analytics engine is implemented in `backend/app/analytics_engine.py` and is invoked by the `/analytics/metrics` endpoint. It loads the latest ingested data, builds a directed graph, computes centrality metrics (degree, eigenvector, authority, hub), and assigns a risk score to each node. All scripts and data flows are documented for reproducibility.

### Reproducibility Checklist
- All ingestion, analytics, and sync scripts are versioned in `backend/app/`
- API endpoints are documented here and in OpenAPI docs (`/docs`)
- Environment setup is reproducible via Docker and requirements.txt
- Data model mapping and architecture are described below

### Architecture Overview
The analytics engine will use network analysis techniques to characterize critical nodes and forecast risk. Key components:
- **NetworkX**: For graph construction and centrality calculations (degree, eigenvector, authority, betweenness, etc.)
- **Neo4j**: For persistent graph storage and complex queries
- **Overlay Data**: Macro forces (unemployment, company finances, location, demand) will be integrated as node/edge attributes
- **Risk Forecasting**: Combine network metrics and macro data to generate risk scores and forecasts

### Required Libraries
- networkx
- numpy, pandas (for data manipulation)
- scikit-learn (for risk modeling, optional)
- neo4j
- fastapi (API layer)

### Integration Points
- API endpoints for analytics (see above)
- Data ingestion from external sources (Finnhub, SEC EDGAR, USAspending, OpenCorporates)
- Frontend visualizations (React, D3.js, etc.)

### Example Workflow
1. Ingest supply chain and macro data
2. Build/augment network graph
3. Calculate centrality and other metrics
4. Overlay macro forces
5. Generate risk scores and forecasts
6. Expose results via API and frontend

### Next Steps
- Define risk scoring models and forecasting logic
- Prototype analytics engine in backend/app/app.py
- Integrate with Neo4j and external data sources

---

# Phase Two: Research & Planning for Core Analytics Engine

## 1. Selected Open-Source APIs & Data Sources
- **USAspending ORM**: For U.S. federal contract awards, agencies, program offices, primes, and suppliers.
- **SEC EDGAR**: For public company filings, subsidiary relationships, and parent-child corporate structures.
- **OpenCorporates**: For global business entity data, corporate groupings, and ownership.
- **Finnhub**: For supplier/customer relationships, financials, and market data.

## 2. Analytics Approach (Core Engine)
- **Directed Graph Model**: Use NetworkX DiGraph to represent the industrial network.
  - **Nodes**: Entities (funding agencies, program offices, primes, suppliers, subsidiaries) with unique IDs and attributes (type, name, sector, location, etc).
  - **Edges**: Directed, with attributes such as contract value, type (prime_contract, subcontract, subsidiary), and commodity.
- **Centrality & Risk Metrics**:
  - Compute degree, eigenvector, and authority centrality for each node.
  - Quantify systemic risk using centrality-based measures (see referenced GWU thesis for methodology).
  - Overlay macroeconomic and financial data as node/edge attributes for risk forecasting.
- **Data Ingestion**:
  - Extract and normalize entities and relationships from APIs.
  - Map contract award flows: Funding Agency → Sub-Agency/Program Office → Prime → Supplier/Subcontractor.
  - Augment with subsidiary and ownership edges from SEC EDGAR and OpenCorporates.

## 3. High-Level Architecture
```
+-------------------+      +-------------------+      +-------------------+
|  Data Ingestion   | ---> |   Graph Builder   | ---> | Analytics Engine  |
+-------------------+      +-------------------+      +-------------------+
        |                        |                          |
        v                        v                          v
  [APIs: USAspending,      [NetworkX DiGraph]         [Centrality, Risk
   SEC EDGAR, etc.]                                  Computation, Forecast]
        |                        |                          |
        +------------------------+--------------------------+
                                 |
                                 v
                        [Neo4j Graph DB]
                                 |
                                 v
                        [API Layer (FastAPI)]
                                 |
                                 v
                        [Frontend Visualization]
```

- **Data Ingestion**: Scripts/services to pull and normalize data from APIs.
- **Graph Builder**: Constructs/updates the directed network in NetworkX and Neo4j.
- **Analytics Engine**: Computes centrality, risk, and overlays macro data.
- **API Layer**: Exposes analytics and network data to frontend.
- **Frontend**: Visualizes network, metrics, and risk forecasts.

## 4. Success Criteria
- Core analytics engine computes centrality and risk metrics on real data.
- Directed network accurately represents funding flows and supplier relationships.
- APIs and ingestion scripts are documented and reproducible.
- Application is ready for initial testing and further feature development.

## 5. References
- [GWU Thesis: Quantifying Systemic Risk in Industrial Networks](https://scholarspace.library.gwu.edu/concern/gw_etds/d217qq288)
- See oluo_network-method.txt for node/edge design vision.

---

## API Data Model Mapping

### USAspending ORM
- **Nodes**:
  - Funding Agency: {id, name, type}
  - Sub-Agency/Program Office: {id, name, parent_agency_id}
  - Prime Contractor: {duns, name, sector, location}
  - Supplier/Subcontractor: {duns, name, sector, location}
- **Edges**:
  - prime_contract: {from: program_office, to: prime, value, commodity, fiscal_year}
  - subcontract: {from: prime, to: supplier, value, commodity, fiscal_year}

### SEC EDGAR
- **Nodes**:
  - Public Company: {cik, name, sector}
  - Subsidiary: {cik, name, parent_cik}
- **Edges**:
  - subsidiary: {from: parent, to: subsidiary, type: "subsidiary"}

### OpenCorporates
- **Nodes**:
  - Business Entity: {oc_id, name, jurisdiction, sector}
- **Edges**:
  - ownership: {from: parent, to: child, type: "ownership"}

### Finnhub
- **Nodes**:
  - Company: {ticker, name, sector}
- **Edges**:
  - supplier_customer: {from: supplier, to: customer, type: "supply_chain"}
