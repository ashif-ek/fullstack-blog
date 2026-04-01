from __future__ import annotations

from dataclasses import dataclass
from json import dumps

from apps.interactions.selectors import upsert_like_counter
from apps.interactions.utils.rate_limit import is_rate_limited
from core.services.task_dispatcher import enqueue_task_safely
from infra.redis import get_redis_client, safe_redis_call


@dataclass
class LikeResult:
    liked: bool
    count: int
    rate_limited: bool = False


def register_like(*, user_id: int, post_id: int) -> LikeResult:
    if is_rate_limited(user_id=user_id, action="like", limit=30, window_seconds=60):
        return LikeResult(liked=False, count=0, rate_limited=True)

    redis_client = get_redis_client()
    user_set_key = f"likes:set:{post_id}"
    count_key = f"likes:count:{post_id}"
    event_key = f"likes:events:{post_id}"

    pipeline = redis_client.pipeline()
    pipeline.sadd(user_set_key, user_id)
    pipeline.expire(user_set_key, 86400 * 7)
    result = safe_redis_call(pipeline.execute, default=None)

    if result is None:
        return _register_like_db_fallback(post_id=post_id)

    was_added = bool(result[0])
    if was_added:
        count = int(safe_redis_call(redis_client.incr, count_key, default=0) or 0)
        safe_redis_call(
            redis_client.lpush,
            event_key,
            dumps({"event": "like", "post_id": post_id, "user_id": user_id, "count": count}),
            default=None,
        )
        safe_redis_call(redis_client.ltrim, event_key, 0, 2000, default=None)
    else:
        count = int(safe_redis_call(redis_client.get, count_key, default=0) or 0)

    from apps.interactions.tasks import sync_likes_to_db_task

    enqueue_task_safely(sync_likes_to_db_task, post_id, queue="high_priority")
    return LikeResult(liked=was_added, count=count)


def _register_like_db_fallback(*, post_id: int) -> LikeResult:
    from apps.interactions.models import PostLikeCounter

    obj, _ = PostLikeCounter.objects.get_or_create(post_id=post_id, defaults={"count": 0})
    obj.count += 1
    obj.save(update_fields=["count", "updated_at"])
    upsert_like_counter(post_id=post_id, count=obj.count)
    return LikeResult(liked=True, count=obj.count)
