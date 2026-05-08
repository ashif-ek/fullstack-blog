import logging
from json import loads

from celery import shared_task

from infra.celery import ResilientTask
from infra.email import send_platform_email
from infra.redis import get_redis_client, safe_redis_call

from apps.interactions.selectors import upsert_like_counter
from apps.interactions.services.notification_service import (
    buffer_notification,
    flush_buffered_notifications,
)

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=ResilientTask, queue="high_priority")
def sync_likes_to_db_task(self, post_id: int) -> dict:
    from apps.interactions.models import UserPostLike
    redis_client = get_redis_client()
    event_key = f"likes:events:{post_id}"
    
    # Process events from Redis queue
    events_processed = 0
    while True:
        raw_event = safe_redis_call(redis_client.rpop, event_key, default=None)
        if not raw_event:
            break
        
        try:
            event_data = loads(raw_event)
            user_id = event_data.get("user_id")
            event_type = event_data.get("event")
            
            if user_id and event_type == "like":
                UserPostLike.objects.get_or_create(user_id=user_id, post_id=post_id)
            elif user_id and event_type == "unlike":
                UserPostLike.objects.filter(user_id=user_id, post_id=post_id).delete()
            
            events_processed += 1
        except Exception as e:
            logger.error(f"Error processing like event: {e}")

    # Update total count
    count = int(safe_redis_call(redis_client.get, f"likes:count:{post_id}", default=0) or 0)
    upsert_like_counter(post_id=post_id, count=count)
    
    return {"post_id": post_id, "count": count, "events_processed": events_processed}


@shared_task(bind=True, base=ResilientTask, queue="default")
def process_share_event_task(self, payload: dict) -> dict:
    user_id = payload.get("user_id")
    if user_id:
        buffer_notification(
            user_id=user_id,
            payload={"event": "share_recorded", "post_id": payload.get("post_id")},
        )
    return {"status": "processed", "type": "share"}


@shared_task(bind=True, base=ResilientTask, queue="low_priority")
def flush_notifications_task(self, user_id: int, payload: dict | None = None) -> dict:
    if payload:
        buffer_notification(user_id=user_id, payload=payload)
    flushed = flush_buffered_notifications(user_id=user_id)
    return {"user_id": user_id, "flushed": flushed}


@shared_task(bind=True, base=ResilientTask, queue="low_priority")
def replay_fallback_queue_task(self) -> int:
    redis_client = get_redis_client()
    moved = 0

    while True:
        raw_task = safe_redis_call(redis_client.lpop, "celery:fallback_queue", default=None)
        if not raw_task:
            break
        payload = loads(raw_task)
        self.app.send_task(
            payload["task"],
            args=payload.get("args", []),
            kwargs=payload.get("kwargs", {}),
            queue=payload.get("queue", "default"),
            countdown=payload.get("countdown") or 0,
        )
        moved += 1
    return moved


@shared_task(bind=True, base=ResilientTask, queue="low_priority")
def send_notification_email_task(self, recipient: str, subject: str, body: str) -> dict:
    send_platform_email(subject=subject, body=body, recipients=[recipient], fail_silently=False)
    logger.info("Notification email sent", extra={"recipient": recipient})
    return {"recipient": recipient, "status": "sent"}
