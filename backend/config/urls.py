from django.contrib import admin
from django.urls import include, path

from core.health import health_view, ready_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_view, name="health"),
    path("ready/", ready_view, name="ready"),
    path("api/", include("apps.urls")),
]
