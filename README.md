# Supply Chain Network App

A B2B supply chain network app using network analytics, open-source APIs, and Docker for risk management and supplier connections.

## Features

- **FastAPI Backend**: RESTful API with endpoints for network analytics
- **NetworkX Integration**: Graph analysis and network metrics calculation
- **Neo4j Database**: Graph database for storing supply chain relationships
- **Docker Compose**: Multi-container orchestration for easy deployment
- **Frontend Placeholder**: Ready for React app integration

## Architecture

```
├── backend/           # FastAPI backend service
│   ├── app/
│   │   ├── main.py   # Main application with API endpoints
│   │   └── __init__.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/          # Frontend placeholder (React app)
│   ├── Dockerfile
│   ├── index.html    # Placeholder page
│   ├── nginx.conf
│   └── README.md
└── docker-compose.yml # Multi-container orchestration
```

## Quick Start

### Prerequisites

- Docker (20.10+)
- Docker Compose (1.29+)

### Running the Application

1. Clone the repository:
   ```bash
   git clone https://github.com/Oluou/supply-chain-network-app.git
   cd supply-chain-network-app
   ```

2. Start all services:
   ```bash
   docker compose up -d
   ```

3. Access the services:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Neo4j Browser**: http://localhost:7474 (user: neo4j, password: password)

### Stopping the Application

```bash
docker compose down
```

To remove all data:
```bash
docker compose down -v
```

## API Endpoints

### Health Check
- `GET /health` - Check service health

### Network Analytics (NetworkX)
- `POST /network/analyze` - Analyze network metrics (density, centrality, components)
- `POST /network/shortest-path` - Find shortest path between nodes
- `POST /network/centrality` - Calculate centrality metrics

### Neo4j Operations
- `GET /neo4j/nodes` - Get all nodes from database
- `POST /neo4j/create-sample` - Create sample supply chain data

## API Usage Examples

### Analyze Network

```bash
curl -X POST "http://localhost:8000/network/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "nodes": [
      {"id": "SUP1", "type": "Supplier", "name": "Raw Materials Inc"},
      {"id": "MAN1", "type": "Manufacturer", "name": "Assembly Corp"},
      {"id": "DIS1", "type": "Distributor", "name": "Logistics Ltd"}
    ],
    "edges": [
      {"source": "SUP1", "target": "MAN1", "relationship": "SUPPLIES", "weight": 1.0},
      {"source": "MAN1", "target": "DIS1", "relationship": "SHIPS_TO", "weight": 1.5}
    ]
  }'
```

### Find Shortest Path

```bash
curl -X POST "http://localhost:8000/network/shortest-path" \
  -H "Content-Type: application/json" \
  -d '{
    "network_data": {
      "nodes": [
        {"id": "SUP1", "type": "Supplier", "name": "Raw Materials Inc"},
        {"id": "MAN1", "type": "Manufacturer", "name": "Assembly Corp"},
        {"id": "DIS1", "type": "Distributor", "name": "Logistics Ltd"}
      ],
      "edges": [
        {"source": "SUP1", "target": "MAN1", "relationship": "SUPPLIES", "weight": 1.0},
        {"source": "MAN1", "target": "DIS1", "relationship": "SHIPS_TO", "weight": 1.5}
      ]
    },
    "source": "SUP1",
    "target": "DIS1"
  }'
```

### Create Sample Data in Neo4j

```bash
curl -X POST "http://localhost:8000/neo4j/create-sample"
```

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

The frontend is currently a placeholder. To add a React app:

1. Navigate to the frontend folder
2. Generate a React app using create-react-app or GitHub Spark
3. Update the Dockerfile to use the multi-stage build (commented in the file)
4. Rebuild: `docker compose up -d --build frontend`

## Environment Variables

Backend environment variables (set in docker-compose.yml or .env file):
- `NEO4J_URI`: Neo4j connection URI (default: bolt://neo4j:7687)
- `NEO4J_USER`: Neo4j username (default: neo4j)
- `NEO4J_PASSWORD`: Neo4j password (default: password)

**Security Note**: Create a `.env` file based on `.env.example` and update the default credentials before deploying to production.

## Security Considerations

1. **CORS Configuration**: The backend allows all origins by default. In production, update `allow_origins` in `backend/app/main.py` to restrict access to specific domains.
2. **Neo4j Credentials**: Change the default Neo4j credentials in your `.env` file.
3. **Dependencies**: All dependencies are checked for known vulnerabilities. Keep them updated regularly.

## Technologies

- **Backend**: Python 3.11, FastAPI, NetworkX, Neo4j
- **Frontend**: HTML/CSS (placeholder), Nginx
- **Database**: Neo4j 5.15
- **Containerization**: Docker, Docker Compose

## License

See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

