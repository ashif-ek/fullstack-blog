from .base import *  # noqa: F403

DEBUG = True

REDIS_URL = "redis://redis:6379/0"
CACHES["default"] = build_django_cache_config(REDIS_URL)  # noqa: F405
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0"]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
