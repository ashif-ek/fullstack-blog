from __future__ import annotations

import time

from django.core.cache import cache

from infra.redis import get_redis_client, safe_redis_call


def _fallback_key(user_id: int | str, action: str, window_seconds: int) -> str:
    return f"fallback:ratelimit:{user_id}:{action}:{window_seconds}"


def is_rate_limited(
    *,
    user_id: int | str,
    action: str,
    limit: int,
    window_seconds: int,
) -> bool:
    """
    Sliding-window limiter backed by Redis sorted sets.
    Key format: user:{id}:{action}
    """
    redis_key = f"user:{user_id}:{action}"
    now_ms = int(time.time() * 1000)
    window_start = now_ms - (window_seconds * 1000)
    redis_client = get_redis_client()
    member = f"{now_ms}-{time.time_ns()}-{action}"

    pipeline = redis_client.pipeline()
    pipeline.zremrangebyscore(redis_key, 0, window_start)
    pipeline.zadd(redis_key, {member: now_ms})
    pipeline.zcard(redis_key)
    pipeline.expire(redis_key, window_seconds + 5)
    result = safe_redis_call(pipeline.execute, default=None)

    if result is None:
        local_key = _fallback_key(user_id, action, window_seconds)
        count = cache.get(local_key, 0) + 1
        cache.set(local_key, count, timeout=window_seconds)
        return count > limit

    current_count = int(result[2])
    return current_count > limit
