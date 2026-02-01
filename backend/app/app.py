
import os
import httpx

# Finnhub API settings
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "d5qjfahr01qhn30g3dvgd5qjfahr01qhn30g3e00")
FINNHUB_SECRET = os.getenv("FINNHUB_SECRET", "d5qjfahr01qhn30g3e10")
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

def get_finnhub_headers():
    return {
        "X-Finnhub-Secret": FINNHUB_SECRET,
        "Accept": "application/json"
    }

async def finnhub_get(endpoint: str, params: dict = None):
    url = f"{FINNHUB_BASE_URL}/{endpoint}"
    headers = get_finnhub_headers()
    params = params or {}
    params["token"] = FINNHUB_API_KEY
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware







from app.routers import ingestion, graph, neo4j, analytics, risk, nodes, edges

from app.utils.monitoring import router as monitoring_router, track_metrics
from app.utils.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from fastapi.responses import PlainTextResponse
from app.utils.exceptions import add_global_exception_handlers





app = FastAPI(title="Supply Chain Network Analytics API")
app.state.limiter = limiter

# Rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return PlainTextResponse("Rate limit exceeded", status_code=429)

# Global exception handler
add_global_exception_handlers(app)

# CORS: Restrict to trusted origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

track_metrics(app)
app.include_router(ingestion.router)
app.include_router(graph.router)
app.include_router(neo4j.router)
app.include_router(analytics.router)
app.include_router(risk.router)
app.include_router(nodes.router)
app.include_router(edges.router)
app.include_router(monitoring_router)

# Neo4j connection settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
