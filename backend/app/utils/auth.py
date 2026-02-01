
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import os

API_KEY = os.getenv("API_KEY", "changeme-supersecret-key")
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key: str = Depends(api_key_header)):
    # Support for key rotation: allow comma-separated keys
    valid_keys = [k.strip() for k in API_KEY.split(",") if k.strip()]
    if api_key in valid_keys:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
