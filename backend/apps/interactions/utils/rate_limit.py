import time
from django_redis import get_redis_connection
from rest_framework.exceptions import Throttled

class RateLimiter:
    """
    Sliding window rate limiter using Redis ZSET.
    """
    @staticmethod
    def is_allowed(user_id, action, limit=10, window=60):
        """
        Check if user is within the rate limit for a specific action.
        :param user_id: ID of the user
        :param action: Name of the action (e.g., 'like', 'comment')
        :param limit: Max requests allowed in the window
        :param window: Window size in seconds
        :return: True if allowed, False otherwise
        """
        conn = get_redis_connection("default")
        key = f"rate_limit:{user_id}:{action}"
        now = time.time()
        
        # Start a pipeline
        pipe = conn.pipeline()
        
        # Remove timestamps older than the window
        pipe.zremrangebyscore(key, 0, now - window)
        
        # Count remaining timestamps
        pipe.zcard(key)
        
        # Add the current timestamp
        pipe.zadd(key, {now: now})
        
        # Set expiration for the ZSET to cleanup
        pipe.expire(key, window + 10)
        
        # Execute
        _, current_count, _, _ = pipe.execute()
        
        if current_count >= limit:
            return False
        return True

    @classmethod
    def check_rate_limit(cls, user_id, action, limit=10, window=60):
        if not cls.is_allowed(user_id, action, limit, window):
            raise Throttled(detail=f"Rate limit exceeded for {action}. Please try again later.")
