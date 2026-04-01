from __future__ import annotations

import hashlib
import os
from typing import Callable

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, JsonResponse

from infra.redis import get_redis_client, safe_redis_call

IDEMPOTENT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
IDEMPOTENCY_TTL_SECONDS = int(os.getenv("IDEMPOTENCY_TTL_SECONDS", "600"))


class IdempotencyMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.method not in IDEMPOTENT_METHODS or not request.path.startswith("/api/"):
            return self.get_response(request)

        key = request.headers.get("Idempotency-Key")
        if not key:
            return JsonResponse(
                {"detail": "Idempotency-Key header is required for write operations."},
                status=400,
            )

        user_part = "anonymous"
        if hasattr(request, "user") and getattr(request.user, "is_authenticated", False):
            user_part = str(request.user.id)

        request_hash = hashlib.sha256(
            f"{user_part}:{request.method}:{request.path}:{key}".encode("utf-8")
        ).hexdigest()
        redis_key = f"idempotency:{request_hash}"

        redis_client = get_redis_client()
        was_written = safe_redis_call(
            redis_client.set,
            redis_key,
            "1",
            nx=True,
            ex=IDEMPOTENCY_TTL_SECONDS,
            default=None,
        )

        if was_written is None:
            # Redis degraded fallback: local process cache.
            if not cache.add(redis_key, "1", timeout=IDEMPOTENCY_TTL_SECONDS):
                return JsonResponse({"detail": "Duplicate request rejected."}, status=409)
        elif not was_written:
            return JsonResponse({"detail": "Duplicate request rejected."}, status=409)

        return self.get_response(request)
