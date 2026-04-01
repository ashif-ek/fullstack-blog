from django.http import JsonResponse
from django.urls import path


def blog_ping(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("ping/", blog_ping),
]
