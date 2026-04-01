from __future__ import annotations

from django.core.cache import cache

from apps.interactions.selectors import create_comment_record, get_comment_parent, get_comments_page
from apps.interactions.serializers import CommentSerializer
from apps.interactions.utils.rate_limit import is_rate_limited
from core.services.task_dispatcher import enqueue_task_safely

COMMENTS_FIRST_PAGE_CACHE_TTL = 60
COMMENTS_MAX_DEPTH = 3


def list_comments_first_page(*, post_id: int, page_size: int = 20) -> list[dict]:
    cache_key = f"comments:first:{post_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    comments = get_comments_page(post_id=post_id, limit=page_size)
    payload = CommentSerializer(comments, many=True).data
    cache.set(cache_key, payload, timeout=COMMENTS_FIRST_PAGE_CACHE_TTL)
    return payload


def create_comment(
    *,
    user_id: int | None,
    post_id: int,
    body: str,
    parent_id: int | None = None,
) -> dict:
    if user_id and is_rate_limited(user_id=user_id, action="comment", limit=12, window_seconds=60):
        return {"status": "rate_limited"}

    parent = get_comment_parent(parent_id)
    if parent and parent.depth >= COMMENTS_MAX_DEPTH:
        return {"status": "depth_exceeded", "max_depth": COMMENTS_MAX_DEPTH}

    comment = create_comment_record(user_id=user_id, post_id=post_id, body=body, parent=parent)
    cache.delete(f"comments:first:{post_id}")

    from apps.interactions.tasks import flush_notifications_task

    enqueue_task_safely(
        flush_notifications_task,
        user_id or 0,
        {"event": "comment_created", "post_id": post_id, "comment_id": comment.id},
        queue="low_priority",
    )
    return {"status": "ok", "comment": CommentSerializer(comment).data}
