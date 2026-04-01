import os

import redis


def get_redis_url() -> str:
    return os.getenv("REDIS_URL", "")


def build_django_cache_config(redis_url: str) -> dict:
    if not redis_url:
        return {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "fallback-cache",
        }

    return {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": redis_url,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "IGNORE_EXCEPTIONS": True,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "retry_on_timeout": True,
                "health_check_interval": 30,
            },
        },
        "TIMEOUT": 300,
    }


def ping_redis() -> bool:
    redis_url = get_redis_url()
    if not redis_url:
        return False

    try:
        client = redis.Redis.from_url(redis_url, socket_connect_timeout=3, socket_timeout=3)
        return bool(client.ping())
    except Exception:
        return False
