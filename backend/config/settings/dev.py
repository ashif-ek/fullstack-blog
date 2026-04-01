from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0"]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
