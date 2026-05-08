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

    # Check if user already liked
    is_member = safe_redis_call(redis_client.sismember, user_set_key, user_id, default=None)

    if is_member is None:
        # Redis is down, use DB fallback
        return _register_like_db_fallback(user_id=user_id, post_id=post_id)

    if is_member:
        # UNLIKE logic
        pipeline = redis_client.pipeline()
        pipeline.srem(user_set_key, user_id)
        pipeline.decr(count_key)
        result = safe_redis_call(pipeline.execute, default=[0, 0])
        count = int(result[1]) if result else 0
        liked = False
        event_type = "unlike"
    else:
        # LIKE logic
        pipeline = redis_client.pipeline()
        pipeline.sadd(user_set_key, user_id)
        pipeline.incr(count_key)
        pipeline.expire(user_set_key, 86400 * 7)
        result = safe_redis_call(pipeline.execute, default=[0, 0, 0])
        count = int(result[1]) if result else 0
        liked = True
        event_type = "like"

    # Ensure count doesn't go below 0
    if count < 0:
        count = 0
        safe_redis_call(redis_client.set, count_key, 0)

    safe_redis_call(
        redis_client.lpush,
        event_key,
        dumps({"event": event_type, "post_id": post_id, "user_id": user_id, "count": count}),
        default=None,
    )
    safe_redis_call(redis_client.ltrim, event_key, 0, 2000, default=None)

    from apps.interactions.tasks import sync_likes_to_db_task
    enqueue_task_safely(sync_likes_to_db_task, post_id, queue="high_priority")

    return LikeResult(liked=liked, count=count)


def _register_like_db_fallback(*, user_id: int, post_id: int) -> LikeResult:
    from apps.interactions.models import PostLikeCounter, UserPostLike

    # Toggle the individual like record
    like_qs = UserPostLike.objects.filter(user_id=user_id, post_id=post_id)
    if like_qs.exists():
        like_qs.delete()
        change = -1
        liked = False
    else:
        UserPostLike.objects.get_or_create(user_id=user_id, post_id=post_id)
        change = 1
        liked = True

    # Update the counter
    counter, _ = PostLikeCounter.objects.get_or_create(post_id=post_id, defaults={"count": 0})
    counter.count += change
    if counter.count < 0:
        counter.count = 0
    counter.save(update_fields=["count", "updated_at"])
    
    # Sync with our local search/index if needed
    upsert_like_counter(post_id=post_id, count=counter.count)
    
    return LikeResult(liked=liked, count=counter.count)
