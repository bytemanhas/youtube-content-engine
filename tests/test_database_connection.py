import asyncio
import selectors

from sqlalchemy import text

from app.db import engine


async def main() -> None:
    """Verify connectivity to PostgreSQL."""

    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        print(f"PostgreSQL connection successful: {result.scalar_one()}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        ),
    )