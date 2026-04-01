from celery import Task


class ResilientTask(Task):
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 300
    retry_jitter = True
    retry_kwargs = {"max_retries": 5}
    soft_time_limit = 25
    time_limit = 30
