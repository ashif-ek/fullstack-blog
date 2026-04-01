from celery import Task


class ResilientTask(Task):
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    retry_kwargs = {"max_retries": 5}
    soft_time_limit = 60
    time_limit = 90
