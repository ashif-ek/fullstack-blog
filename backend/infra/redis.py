from __future__ import annotations

import logging
import os
from threading import Lock
from typing import Any, Callable, TypeVar

import redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry

logger = logging.getLogger(__name__)
T = TypeVar("T")

DEFAULT_REDIS_URL = "redis://redis:6379/0"


def get_redis_url() -> str:
    return os.getenv("REDIS_URL", DEFAULT_REDIS_URL)


class RedisManager:
    _instance: "RedisManager | None" = None
    _instance_lock = Lock()

    def __init__(self, redis_url: str) -> None:
        retry = Retry(ExponentialBackoff(cap=2, base=0.1), retries=3)
        self._pool = redis.ConnectionPool.from_url(
            redis_url,
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "200")),
            socket_connect_timeout=2,
            socket_timeout=2,
            retry=retry,
            retry_on_timeout=True,
            health_check_interval=30,
            decode_responses=True,
        )
        self._client = redis.Redis(connection_pool=self._pool)

    @classmethod
    def get_instance(cls) -> "RedisManager":
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls(get_redis_url())
        return cls._instance

    @property
    def client(self) -> redis.Redis:
        return self._client

    def ping(self) -> bool:
        try:
            return bool(self._client.ping())
        except redis.RedisError:
            return False


def get_redis_client() -> redis.Redis:
    return RedisManager.get_instance().client


def safe_redis_call(callable_fn: Callable[..., T], *args: Any, default: T | None = None, **kwargs: Any) -> T | None:
    try:
        return callable_fn(*args, **kwargs)
    except redis.RedisError:
        logger.warning("Redis operation failed; fallback path enabled", exc_info=True)
        return default


def build_django_cache_config(redis_url: str) -> dict[str, Any]:
    return {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": redis_url,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 3,
            "SOCKET_TIMEOUT": 3,
            "IGNORE_EXCEPTIONS": True,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": int(os.getenv("REDIS_MAX_CONNECTIONS", "200")),
                "retry_on_timeout": True,
                "health_check_interval": 30,
            },
        },
        "TIMEOUT": 300,
    }


def ping_redis() -> bool:
    return RedisManager.get_instance().ping()
