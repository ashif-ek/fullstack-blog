from __future__ import annotations

from json import dumps, loads

from apps.interactions.models import NotificationDigest
from infra.redis import get_redis_client, safe_redis_call


def buffer_notification(*, user_id: int, payload: dict) -> None:
    redis_client = get_redis_client()
    key = f"notifications:buffer:{user_id}"
    safe_redis_call(redis_client.rpush, key, dumps(payload), default=None)
    safe_redis_call(redis_client.expire, key, 3600, default=None)


def flush_buffered_notifications(*, user_id: int, batch_size: int = 50) -> int:
    redis_client = get_redis_client()
    key = f"notifications:buffer:{user_id}"
    events = safe_redis_call(redis_client.lrange, key, 0, batch_size - 1, default=None)

    if events is None:
        return 0
    if not events:
        return 0

    parsed = [loads(item) for item in events]
    NotificationDigest.objects.create(user_id=user_id, payload={"events": parsed})
    safe_redis_call(redis_client.ltrim, key, len(events), -1, default=None)
    return len(events)
