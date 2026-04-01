import logging

from celery import shared_task

from infra.celery import ResilientTask

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=ResilientTask, queue="high_priority")
def high_priority_notification(self, payload: dict) -> dict:
    logger.info("High priority task received", extra={"payload": payload})
    return {"status": "queued", "priority": "high"}


@shared_task(bind=True, base=ResilientTask, queue="default")
def default_priority_job(self, payload: dict) -> dict:
    logger.info("Default priority task received", extra={"payload": payload})
    return {"status": "queued", "priority": "default"}


@shared_task(bind=True, base=ResilientTask, queue="low_priority")
def low_priority_cleanup(self, payload: dict) -> dict:
    logger.info("Low priority task received", extra={"payload": payload})
    return {"status": "queued", "priority": "low"}
