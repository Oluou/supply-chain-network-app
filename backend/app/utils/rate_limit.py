from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

# Allow 100 requests per minute per IP by default
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Usage: add @limiter.limit("10/minute") to endpoints if needed
