import logging

from fastapi import FastAPI

from app.config import get_settings
from app.logging_config import configure_logging


configure_logging()

settings = get_settings()

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="Autonomous YouTube content generation and optimization engine.",
    version=settings.app_version,
)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize application services."""
    logger.info(
        "YouTube Content Engine starting | environment=%s | version=%s",
        settings.environment,
        settings.app_version,
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Return the health status of the API."""
    logger.info("Health check requested")
    return {"status": "ok"}