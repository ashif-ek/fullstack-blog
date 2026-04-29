from django.http import JsonResponse
from django.urls import include, path

def api_root(request):
    return JsonResponse({
        "message": "Welcome to the Blog API",
        "documentation": "/api/docs/",
        "endpoints": {
            "accounts": "/api/register/",
            "blog": "/api/blog/",
            "interactions": "/api/interactions/"
        }
    })

urlpatterns = [
    path("", api_root),
    path("", include("apps.accounts.urls")),
    path("blog/", include("apps.blog.urls")),
    path("interactions/", include("apps.interactions.urls")),
]
