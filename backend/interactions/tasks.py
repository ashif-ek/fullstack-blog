from celery import shared_task
from django_redis import get_redis_connection
from django.db import transaction
from blog.models import Post
from .models import Like, Share, Notification
from .services import NotificationService

@shared_task(name="interactions.tasks.sync_likes_to_db")
def sync_likes_to_db():
    """
    Periodic task to sync Redis like counts and user sets to PostgreSQL.
    """
    conn = get_redis_connection("default")
    # Get all count keys
    count_keys = conn.keys("post:*:likes")
    
    for key in count_keys:
        try:
            # key is bytes, e.g. b'post:1:likes'
            if isinstance(key, bytes):
                key_str = key.decode("utf-8")
            else:
                key_str = key
                
            post_id = key_str.split(":")[1]
            redis_count = int(conn.get(key) or 0)
            
            # Sync count to Post model
            with transaction.atomic():
                try:
                    post = Post.objects.select_for_update().get(pk=post_id)
                except Post.DoesNotExist:
                    continue
                    
                post.likes_count = redis_count
                post.save()
                
                # Also sync 'who' liked it from the set
                users_key = f"post:{post_id}:liked_users"
                user_ids = conn.smembers(users_key)
                
                # Batch create Like objects for users in Redis set that aren't in DB yet
                existing_likes = set(Like.objects.filter(post_id=post_id).values_list('user_id', flat=True))
                new_likes = [
                    Like(post_id=post_id, user_id=int(u_id)) 
                    for u_id in user_ids 
                    if int(u_id) not in existing_likes
                ]
                Like.objects.bulk_create(new_likes, ignore_conflicts=True)
                
                # Handle removals: If user is in DB but NOT in Redis set, they unliked
                redis_user_ids = {int(u_id) for u_id in user_ids}
                Like.objects.filter(post_id=post_id).exclude(user_id__in=redis_user_ids).delete()
                
        except Exception as e:
            # In production, use standard logging
            print(f"Error syncing likes for {key}: {e}")

@shared_task(name="interactions.tasks.send_interaction_notification")
def send_interaction_notification(recipient_id, actor_id, verb, target_post_id):
    NotificationService.create_notification(recipient_id, actor_id, verb, target_post_id)

@shared_task(name="interactions.tasks.process_share_event")
def process_share_event(post_id, user_id, shared_to):
    Share.objects.create(post_id=post_id, user_id=user_id, shared_to=shared_to)
    # Trigger notification to author
    try:
        post = Post.objects.get(pk=post_id)
        if post.author_id != user_id:
            send_interaction_notification.delay(post.author_id, user_id, 'share', post_id)
    except Post.DoesNotExist:
        pass
