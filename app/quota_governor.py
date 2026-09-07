from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import logging

from redis.asyncio import Redis


logger = logging.getLogger(__name__)


class QuotaExceededException(Exception):
    """Raised when an operation would exceed its configured quota."""

    def __init__(
        self,
        operation_type: str,
        requested: int,
        remaining: int,
    ) -> None:
        self.operation_type = operation_type
        self.requested = requested
        self.remaining = remaining

        super().__init__(
            f"Quota exceeded for '{operation_type}': "
            f"requested={requested}, remaining={remaining}"
        )


@dataclass(frozen=True, slots=True)
class QuotaBucket:
    """Configuration for a single quota bucket."""

    name: str
    limit: int
    window_seconds: int


class QuotaGovernor:
    """Redis-backed quota manager for external service operations."""

    _CONSUME_SCRIPT = """
    local current = redis.call('GET', KEYS[1])

    if not current then
        current = 0
    else
        current = tonumber(current)
    end

    local requested = tonumber(ARGV[1])
    local limit = tonumber(ARGV[2])

    if current + requested > limit then
        return -1
    end

    local updated = redis.call('INCRBY', KEYS[1], requested)

    if updated == requested then
        redis.call('EXPIRE', KEYS[1], tonumber(ARGV[3]))
    end

    return updated
    """

    def __init__(
        self,
        redis: Redis,
        *,
        key_prefix: str = "youtube-engine:quota",
    ) -> None:
        self._redis = redis
        self._key_prefix = key_prefix.rstrip(":")

    @staticmethod
    def _current_window() -> tuple[str, int]:
        """Return the current UTC date and seconds until midnight."""

        now = datetime.now(UTC)

        tomorrow = (now + timedelta(days=1)).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        ttl = max(1, int((tomorrow - now).total_seconds()))

        return now.strftime("%Y-%m-%d"), ttl

    def _build_key(self, bucket_name: str) -> tuple[str, int]:
        """Build the Redis key for the current quota window."""

        window, ttl = self._current_window()

        key = f"{self._key_prefix}:{bucket_name}:{window}"

        return key, ttl

    async def consume_quota(
        self,
        operation_type: str,
        cost: int,
        bucket: QuotaBucket,
    ) -> bool:
        """Atomically consume quota for an operation."""

        if not operation_type.strip():
            raise ValueError("operation_type cannot be empty.")

        if cost <= 0:
            raise ValueError("cost must be greater than zero.")

        if bucket.limit <= 0:
            raise ValueError("quota limit must be greater than zero.")

        if bucket.window_seconds <= 0:
            raise ValueError("quota window must be greater than zero.")

        if cost > bucket.limit:
            raise QuotaExceededException(
                operation_type=operation_type,
                requested=cost,
                remaining=bucket.limit,
            )

        key, window_ttl = self._build_key(bucket.name)

        ttl = min(bucket.window_seconds, window_ttl)

        result = await self._redis.eval(
            self._CONSUME_SCRIPT,
            1,
            key,
            cost,
            bucket.limit,
            ttl,
        )

        consumed = int(result)

        if consumed == -1:
            current = await self._redis.get(key)
            used = int(current or 0)
            remaining = max(0, bucket.limit - used)

            logger.warning(
                "Quota exceeded | operation=%s | requested=%d | "
                "remaining=%d | bucket=%s",
                operation_type,
                cost,
                remaining,
                bucket.name,
            )

            raise QuotaExceededException(
                operation_type=operation_type,
                requested=cost,
                remaining=remaining,
            )

        logger.info(
            "Quota consumed | operation=%s | cost=%d | "
            "used=%d | remaining=%d | bucket=%s",
            operation_type,
            cost,
            consumed,
            bucket.limit - consumed,
            bucket.name,
        )

        return True

    async def get_remaining(
        self,
        bucket: QuotaBucket,
    ) -> int:
        """Return the remaining quota in the current window."""

        if bucket.limit <= 0:
            raise ValueError("quota limit must be greater than zero.")

        key, _ = self._build_key(bucket.name)

        current = await self._redis.get(key)

        if current is None:
            return bucket.limit

        used = int(current)

        return max(0, bucket.limit - used)