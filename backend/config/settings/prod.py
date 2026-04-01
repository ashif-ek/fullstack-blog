import os

from .base import *  # noqa: F403

DEBUG = False

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL must be set in production.")

if DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
    raise RuntimeError("SQLite is not allowed for production deployments.")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS")  # noqa: F405
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")  # noqa: F405
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")  # noqa: F405
