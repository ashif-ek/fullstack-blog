from django.http import JsonResponse
from django.urls import path


def interactions_ping(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("ping/", interactions_ping),
]
