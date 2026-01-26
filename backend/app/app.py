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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
import networkx as nx
from neo4j import GraphDatabase
import os

# Neo4j connection settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
