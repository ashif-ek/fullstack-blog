from __future__ import annotations

import logging
from collections.abc import Iterable

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_platform_email(
    *,
    subject: str,
    body: str,
    recipients: Iterable[str],
    html_message: str | None = None,
    fail_silently: bool = False,
) -> int:
    recipient_list = list(recipients)
    if not recipient_list:
        return 0

    return send_mail(
        subject=subject,
        message=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=recipient_list,
        fail_silently=fail_silently,
        html_message=html_message,
    )


@shared_task(
    bind=True,
    queue="low_priority",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def send_platform_email_task(
    self,
    *,
    subject: str,
    body: str,
    recipients: list[str],
    html_message: str | None = None,
) -> int:
    logger.info("Sending async platform email", extra={"recipient_count": len(recipients)})
    return send_platform_email(
        subject=subject,
        body=body,
        recipients=recipients,
        html_message=html_message,
        fail_silently=False,
    )


def send_platform_email_async(
    *,
    subject: str,
    body: str,
    recipients: Iterable[str],
    html_message: str | None = None,
) -> None:
    send_platform_email_task.delay(
        subject=subject,
        body=body,
        recipients=list(recipients),
        html_message=html_message,
    )
