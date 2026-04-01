import json
import time
from django_redis import get_redis_connection
from django.db import transaction
from django.conf import settings
from blog.models import Post
from ..models import Like

class LikeService:
    """
    Production-grade Like service with WAL (Write-Ahead Log) pattern.
    Handles high-throughput likes with Redis buffering and DB fallback.
    """
    @staticmethod
    def _get_keys(post_id):
        return {
            "count": f"post:{post_id}:likes_count",
            "users": f"post:{post_id}:liked_users",
            "log": f"post:{post_id}:likes_log",
            "lock": f"post:{post_id}:lock"
        }

    @classmethod
    def toggle_like(cls, post_id, user_id):
        """
        Main entry point for toggling likes.
        """
        try:
            conn = get_redis_connection("default")
            keys = cls._get_keys(post_id)
            
            # 1. Idempotency check in Redis Set
            is_liked = conn.sismember(keys["users"], user_id)
            action = "unlike" if is_liked else "like"
            
            # 2. Write-Ahead Log (WAL) for Celery sync
            event = {
                "user_id": user_id,
                "action": action,
                "timestamp": time.time()
            }
            
            # Atomic operation in Redis
            pipe = conn.pipeline()
            if action == "like":
                pipe.sadd(keys["users"], user_id)
                pipe.incr(keys["count"])
            else:
                pipe.srem(keys["users"], user_id)
                pipe.decr(keys["count"])
            
            pipe.lpush(keys["log"], json.dumps(event))
            pipe.execute()
            
            return {
                "count": int(conn.get(keys["count"]) or 0),
                "is_liked": action == "like",
                "buffered": True
            }

        except Exception as e:
            # FAILURE FALLBACK: Direct DB write if Redis is down
            print(f"Redis failure in LikeService: {e}")
            return cls._fallback_toggle_db(post_id, user_id)

    @classmethod
    def _fallback_toggle_db(cls, post_id, user_id):
        """
        Strongly consistent fallback for Redis failures.
        """
        with transaction.atomic():
            post = Post.objects.select_for_update().get(pk=post_id)
            like_exists = Like.objects.filter(post=post, user_id=user_id).exists()
            
            if like_exists:
                Like.objects.filter(post=post, user_id=user_id).delete()
                post.likes_count = max(0, post.likes_count - 1)
                is_liked = False
            else:
                Like.objects.create(post=post, user_id=user_id)
                post.likes_count += 1
                is_liked = True
            
            post.save()
            return {
                "count": post.likes_count,
                "is_liked": is_liked,
                "buffered": False
            }

    @classmethod
    def get_status(cls, post_id, user_id=None):
        try:
            conn = get_redis_connection("default")
            keys = cls._get_keys(post_id)
            
            count = conn.get(keys["count"])
            if count is None:
                # Cache miss: load from DB
                post = Post.objects.get(pk=post_id)
                count = post.likes_count
                conn.setex(keys["count"], 3600, count) # 1h TTL for count
                
            is_liked = False
            if user_id:
                is_liked = conn.sismember(keys["users"], user_id)
                
            return {
                "count": int(count),
                "is_liked": bool(is_liked)
            }
        except Exception:
            # Fallback for GET status
            post = Post.objects.get(pk=post_id)
            is_liked = Like.objects.filter(post=post, user_id=user_id).exists() if user_id else False
            return {
                "count": post.likes_count,
                "is_liked": is_liked
            }
