import os

from celery import Celery

from infra.celery import ResilientTask

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "config.settings.dev"),
)

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.Task = ResilientTask
app.autodiscover_tasks()
