import logging

from fastapi import FastAPI
from sqlalchemy import text
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.config import get_settings
from app.logging_config import configure_logging
from app.models import Video, VideoStatus
from sqlalchemy import select
from redis.asyncio import Redis

from app.redis_client import get_redis



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
@app.get("/health/database")
async def database_health_check(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    """Verify application-level PostgreSQL connectivity."""

    result = await session.execute(text("SELECT 1"))
    value = result.scalar_one()

    if value != 1:
        raise RuntimeError("Database health check returned an unexpected value.")

    logger.info("Database health check successful")

    return {"status": "ok", "database": "connected"}

    try:
        # CREATE
        session.add(video)
        await session.commit()
        await session.refresh(video)

        created_id = video.id

        # READ
        result = await session.execute(
            select(Video).where(Video.id == created_id)
        )
        stored_video = result.scalar_one()

        # UPDATE
        stored_video.status = VideoStatus.QA_PASSED
        stored_video.title = "Database CRUD Test - Updated"

        await session.commit()
        await session.refresh(stored_video)

        # READ after UPDATE
        result = await session.execute(
            select(Video).where(Video.id == created_id)
        )
        updated_video = result.scalar_one()

        # DELETE
        await session.delete(updated_video)
        await session.commit()

        return {
            "status": "ok",
            "crud": {
                "create": True,
                "read": True,
                "update": True,
                "delete": True,
            },
            "video_id": created_id,
            "final_status": updated_video.status,
        }

    except Exception:
        await session.rollback()
        logger.exception("Database CRUD test failed")
        raise
@app.get("/health/redis")
async def redis_health_check(
    client: Redis = Depends(get_redis),
) -> dict[str, str]:
    """Verify application-level Redis connectivity."""

    try:
        is_connected = await client.ping()

        if not is_connected:
            raise RuntimeError("Redis health check failed.")

        logger.info("Redis health check successful")

        return {
            "status": "ok",
            "redis": "connected",
        }

    except Exception:
        logger.exception("Redis health check failed")
        raise