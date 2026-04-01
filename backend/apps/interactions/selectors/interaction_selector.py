from __future__ import annotations

from django.db import transaction

from apps.interactions.models import Comment, PostLikeCounter


def get_comment_parent(parent_id: int | None) -> Comment | None:
    if not parent_id:
        return None
    return Comment.objects.filter(id=parent_id).first()


@transaction.atomic
def create_comment_record(
    *,
    user_id: int | None,
    post_id: int,
    body: str,
    parent: Comment | None,
) -> Comment:
    return Comment.objects.create(
        user_id=user_id,
        post_id=post_id,
        body=body,
        parent=parent,
    )


def get_comments_page(*, post_id: int, limit: int = 20) -> list[Comment]:
    return list(
        Comment.objects.select_related("user", "parent")
        .filter(post_id=post_id)
        .order_by("-created_at")[:limit]
    )


def upsert_like_counter(*, post_id: int, count: int) -> None:
    PostLikeCounter.objects.update_or_create(post_id=post_id, defaults={"count": count})
