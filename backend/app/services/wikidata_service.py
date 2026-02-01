# Service for Wikidata integration (SPARQL queries)
import httpx

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

class WikidataService:
    async def query(self, sparql_query: str):
        headers = {"Accept": "application/sparql-results+json"}
        async with httpx.AsyncClient() as client:
            response = await client.get(WIKIDATA_SPARQL_URL, params={"query": sparql_query}, headers=headers)
            response.raise_for_status()
            return response.json()
