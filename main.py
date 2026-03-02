# main.py
"""Entry point for running the FastAPI server."""

import os
import uvicorn
from src.config import settings

if __name__ == "__main__":
    # Railway sets PORT env var; fall back to config value
    port = int(os.environ.get("PORT", settings.api_port))
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=port,
        reload=True if settings.environment == "development" else False,
        log_level=settings.log_level.lower()
    )