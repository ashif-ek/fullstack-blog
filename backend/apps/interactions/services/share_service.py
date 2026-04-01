from __future__ import annotations

from json import dumps

from core.services.task_dispatcher import enqueue_task_safely
from infra.redis import get_redis_client, safe_redis_call


def register_share(*, user_id: int | None, post_id: int, channel: str = "") -> None:
    redis_client = get_redis_client()
    key = "shares:events"
    payload = {"event": "share", "post_id": post_id, "user_id": user_id, "channel": channel}
    safe_redis_call(redis_client.rpush, key, dumps(payload), default=None)

    from apps.interactions.tasks import process_share_event_task

    enqueue_task_safely(process_share_event_task, payload, queue="default")
