import json
import logging
from celery import shared_task
from django_redis import get_redis_connection
from django.db import transaction, models
from blog.models import Post
from .models import Like, Notification
from .services.notification_service import NotificationService
from .services.like_service import LikeService

logger = logging.getLogger(__name__)

@shared_task(name="interactions.tasks.sync_likes_worker", queue="high_priority", acks_late=True)
def sync_likes_worker():
    """
    Reads batched events from Redis log and syncs to PostgreSQL.
    Uses distributed locking for race safety.
    """
    conn = get_redis_connection("default")
    # Get all log keys: post:*:likes_log
    log_keys = conn.keys("post:*:likes_log")
    
    for key in log_keys:
        try:
            if isinstance(key, bytes):
                key_str = key.decode("utf-8")
            else:
                key_str = key
                
            post_id = key_str.split(":")[1]
            lock_key = f"post:{post_id}:lock"
            
            # Acquire distributed lock (TTL 10s)
            with conn.lock(lock_key, timeout=10, blocking=False) as lock:
                # 1. Pop all events from the log
                events = []
                while True:
                    event = conn.rpop(key)
                    if not event:
                        break
                    events.append(json.loads(event))
                    
                if not events:
                    continue
                
                # 2. Batch process events
                with transaction.atomic():
                    post = Post.objects.select_for_update().get(pk=post_id)
                    
                    for event in events:
                        user_id = event["user_id"]
                        action = event["action"]
                        
                        if action == "like":
                            _, created = Like.objects.get_or_create(post=post, user_id=user_id)
                            if created:
                                # Count update only if DB record created
                                post.likes_count += 1
                        elif action == "unlike":
                            deleted, _ = Like.objects.filter(post=post, user_id=user_id).delete()
                            if deleted:
                                post.likes_count = max(0, post.likes_count - 1)
                                
                    post.save()
                    logger.info(f"Synced {len(events)} likes for post {post_id}")
                    
        except Exception as e:
            logger.error(f"Error in sync_likes_worker for {key}: {e}")
            # In real prod, put failed events back in log or to a dead-letter queue


@shared_task(name="interactions.tasks.reconciliation_job", queue="default")
def reconciliation_job():
    """
    Periodic job to fix counts if Redis and DB drift.
    """
    conn = get_redis_connection("default")
    # Iterate through all posts with likes
    posts = Post.objects.filter(likes_count__gt=0)
    
    for post in posts:
        db_count = Like.objects.filter(post=post).count()
        if db_count != post.likes_count:
            post.likes_count = db_count
            post.save()
            logger.warning(f"Reconciled post {post.id} count: {db_count}")
            
        # Also sync to Redis if key exists
        count_key = f"post:{post.id}:likes_count"
        if conn.exists(count_key):
            conn.set(count_key, db_count)


@shared_task(name="interactions.tasks.notification_aggregator", queue="low_priority")
def notification_aggregator():
    """
    Aggregates buffered notifications and saves to DB.
    """
    conn = get_redis_connection("default")
    # Identify users with pending notifications
    buffer_keys = conn.keys("notification:*:buffer")
    
    for key in buffer_keys:
        try:
            if isinstance(key, bytes):
                user_id = key.decode("utf-8").split(":")[1]
            else:
                user_id = key.split(":")[1]
                
            NotificationService.aggregate_and_save(int(user_id))
        except Exception as e:
            logger.error(f"Error in notification_aggregator for {key}: {e}")
