import asyncio

from app.config import get_settings
from app.quota_governor import (
    QuotaBucket,
    QuotaExceededException,
    QuotaGovernor,
)
from app.redis_client import redis_client


async def main() -> None:
    """Verify Redis-backed quota enforcement."""

    settings = get_settings()

    bucket = QuotaBucket(
        name="test-enforcement",
        limit=500,
        window_seconds=settings.quota_default_window_seconds,
    )

    governor = QuotaGovernor(redis_client)

    key, _ = governor._build_key(bucket.name)

    try:
        await redis_client.delete(key)

        remaining_before = await governor.get_remaining(bucket)

        await governor.consume_quota(
            operation_type="test_operation",
            cost=400,
            bucket=bucket,
        )

        remaining_after_first = await governor.get_remaining(bucket)

        print(f"Remaining before: {remaining_before}")
        print(
            "Remaining after first consumption: "
            f"{remaining_after_first}"
        )

        try:
            await governor.consume_quota(
                operation_type="test_operation",
                cost=200,
                bucket=bucket,
            )

            raise AssertionError(
                "Quota enforcement failed: operation was allowed."
            )

        except QuotaExceededException as exc:
            print("Quota enforcement successful.")
            print(f"Operation: {exc.operation_type}")
            print(f"Requested: {exc.requested}")
            print(f"Remaining: {exc.remaining}")

    finally:
        await redis_client.delete(key)
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())