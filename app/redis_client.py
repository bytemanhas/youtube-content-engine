from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.config import get_settings


settings = get_settings()


redis_client: Redis = Redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    health_check_interval=30,
)


async def get_redis() -> AsyncGenerator[Redis, None]:
    """Provide the shared asynchronous Redis client."""

    yield redis_client


async def close_redis() -> None:
    """Close the Redis connection pool."""

    await redis_client.aclose()