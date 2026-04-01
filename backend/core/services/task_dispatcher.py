import logging
from typing import Any

from celery.app.task import Task

logger = logging.getLogger(__name__)


def enqueue_task_safely(
    task: Task,
    *args: Any,
    queue: str = "default",
    countdown: int | None = None,
    **kwargs: Any,
):
    """
    Enqueue Celery work without failing the request path when the broker is unavailable.
    Returns AsyncResult on success, None on fallback.
    """
    try:
        return task.apply_async(args=args, kwargs=kwargs, queue=queue, countdown=countdown)
    except Exception:
        logger.exception(
            "Celery enqueue failed; task execution deferred",
            extra={"task_name": task.name, "queue": queue},
        )
        return None
