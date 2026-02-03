from django.core.cache import cache
from django.http import JsonResponse
from functools import wraps


def rate_limit(requests_per_minute=60):
    """
    Decorator to rate limit requests per IP per minute.
    Returns HTTP 429 if limit is exceeded.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Get IP address
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]
            else:
                ip = request.META.get("REMOTE_ADDR")

            # Create a cache key specific to the IP and the view function potentially?
            # Or just global IP rate limit? Request says "per IP per minute".
            # Usually strict per endpoint is safer to avoid blocking whole site.
            # But simple requirement implies global or simple key.
            # Let's use IP + specific decorator usage to be safe contextually?
            # Or simplified: `ratelimit:{ip}`?
            # If we reuse this decorator on multiple views, `ratelimit:{ip}` would share the quota across all decorated views.
            # This is often desired for API wide limits, but "per IP per minute" often implies "rate of requests".
            # Let's allow sharing quota for now as it's a simple implementation.

            cache_key = f"ratelimit:{ip}"

            # Simple timestamp-based distinct window or sliding window?
            # Fixed window is easiest with Django cache `incr`.

            # Logic:
            # We need to expire the key after 60 seconds.
            # But `incr` on non-existent key fails or we set safely.

            # Get current count
            request_count = cache.get(cache_key, 0)

            if request_count >= requests_per_minute:
                return JsonResponse(
                    {"success": False, "error": "Rate limit exceeded"}, status=429
                )

            # Increment
            if request_count == 0:
                cache.set(cache_key, 1, timeout=60)
            else:
                cache.incr(cache_key)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
