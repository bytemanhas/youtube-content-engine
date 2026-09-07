import asyncio

from app.redis_client import redis_client


async def main() -> None:
    """Verify connectivity to Redis."""

    result = await redis_client.ping()
    print(f"Redis connection successful: {result}")

    await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())