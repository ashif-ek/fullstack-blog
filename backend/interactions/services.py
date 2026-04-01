from django_redis import get_redis_connection
from .models import Like, Share, Notification, Comment
from blog.models import Post
from django.conf import settings

User = settings.AUTH_USER_MODEL

class LikeService:
    @staticmethod
    def _get_keys(post_id):
        return {
            "count_key": f"post:{post_id}:likes",
            "users_key": f"post:{post_id}:liked_users",
        }

    @classmethod
    def add_like(cls, post_id, user_id):
        conn = get_redis_connection("default")
        keys = cls._get_keys(post_id)
        
        # Add user to set (SADD returns 1 if added, 0 if already exists)
        if conn.sadd(keys["users_key"], user_id):
            conn.incr(keys["count_key"])
            return True
        return False

    @classmethod
    def remove_like(cls, post_id, user_id):
        conn = get_redis_connection("default")
        keys = cls._get_keys(post_id)
        
        if conn.srem(keys["users_key"], user_id):
            conn.decr(keys["count_key"])
            return True
        return False

    @classmethod
    def get_likes_data(cls, post_id, user_id=None):
        conn = get_redis_connection("default")
        keys = cls._get_keys(post_id)
        
        count = conn.get(keys["count_key"])
        if count is None:
            # Fallback to DB if Redis is empty (init scenario)
            count = Post.objects.get(pk=post_id).likes_set.count()
            conn.set(keys["count_key"], count)
        
        is_liked = False
        if user_id:
            is_liked = conn.sismember(keys["users_key"], user_id)
            
        return {
            "count": int(count),
            "is_liked": bool(is_liked)
        }


class NotificationService:
    @staticmethod
    def create_notification(recipient_id, actor_id, verb, target_post_id):
        # This will be called from a Celery task
        Notification.objects.create(
            recipient_id=recipient_id,
            actor_id=actor_id,
            verb=verb,
            target_post_id=target_post_id
        )


class CommentService:
    @staticmethod
    def get_comment_cache_key(post_id):
        return f"post:{post_id}:comments_cache"

    @classmethod
    def cache_hot_comments(cls, post_id, comments_data):
        conn = get_redis_connection("default")
        key = cls.get_comment_cache_key(post_id)
        # Store top comments for 5 minutes
        conn.set(key, comments_data, ex=300)

    @classmethod
    def get_cached_comments(cls, post_id):
        conn = get_redis_connection("default")
        key = cls.get_comment_cache_key(post_id)
        return conn.get(key)
