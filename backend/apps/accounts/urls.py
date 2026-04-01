from django.http import JsonResponse
from django.urls import path


def accounts_ping(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("accounts/ping/", accounts_ping),
]
