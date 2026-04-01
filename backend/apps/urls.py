from django.urls import include, path

urlpatterns = [
    path("", include("apps.accounts.urls")),
    path("blog/", include("apps.blog.urls")),
    path("interactions/", include("apps.interactions.urls")),
]
