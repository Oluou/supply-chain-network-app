from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("uvicorn.error")

def add_global_exception_handlers(app):
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
