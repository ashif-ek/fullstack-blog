import logging
import time

from django.core.cache import caches
from django.db import connection
from django.http import JsonResponse

from infra.redis import ping_redis

logger = logging.getLogger(__name__)


def health_view(_request):
    return JsonResponse({"status": "ok"})


def ready_view(_request):
    started_at = time.perf_counter()
    checks = {"database": "ok", "cache": "ok"}
    details = {}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
    except Exception as exc:
        checks["database"] = "error"
        details["database_error"] = str(exc)
        logger.exception("Database readiness probe failed")

    try:
        cache = caches["default"]
        cache.set("health:ready", "ok", timeout=5)
        cache.get("health:ready")
        if not ping_redis():
            checks["cache"] = "degraded"
            details["cache_warning"] = "Redis ping failed; cache fallback is active."
    except Exception as exc:
        checks["cache"] = "degraded"
        details["cache_warning"] = str(exc)
        logger.warning("Cache readiness probe failed; fallback mode enabled", exc_info=True)

    duration_ms = int((time.perf_counter() - started_at) * 1000)
    payload = {
        "status": "ready" if checks["database"] == "ok" else "not_ready",
        "checks": checks,
        "duration_ms": duration_ms,
        "details": details,
    }

    status = 200 if checks["database"] == "ok" else 503
    return JsonResponse(payload, status=status)
