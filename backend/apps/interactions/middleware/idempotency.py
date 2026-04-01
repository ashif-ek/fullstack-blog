import hashlib
import json
from django_redis import get_redis_connection
from django.http import JsonResponse

class IdempotencyMiddleware:
    """
    Middleware to handle idempotency using 'Idempotency-Key' header.
    Caches responses in Redis for 24 hours.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.redis = get_redis_connection("default")
        self.TTL = 60 * 60 * 24  # 24 hours

    def __call__(self, request):
        # Only apply to write methods
        if request.method not in ["POST", "PUT", "PATCH", "DELETE"]:
            return self.get_response(request)

        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return self.get_response(request)

        # Create a unique key for Redis - be defensive about request.user
        user = getattr(request, "user", None)
        user_id = user.id if user and user.is_authenticated else "anonymous"
        cache_key = f"idempotency:{user_id}:{idempotency_key}"

        try:
            # Attempt to get cached response
            cached_response = self.redis.get(cache_key)
            if cached_response:
                data = json.loads(cached_response)
                return JsonResponse(
                    data=data["content"],
                    status=data["status"],
                    headers={"X-Idempotency-Cache": "HIT"}
                )

            # Process request
            response = self.get_response(request)

            # Cache original response if it was successful (2xx) or client error (4xx)
            if 200 <= response.status_code < 500:
                try:
                    # Only cache JSON responses
                    content = json.loads(response.content)
                    self.redis.setex(
                        cache_key,
                        self.TTL,
                        json.dumps({
                            "content": content,
                            "status": response.status_code
                        })
                    )
                except (ValueError, TypeError):
                    pass

            return response

        except Exception as e:
            # If Redis fails, just process the request without caching
            print(f"IdempotencyMiddleware Redis Error: {e}")
            return self.get_response(request)
