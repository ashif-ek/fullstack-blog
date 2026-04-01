from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LikeToggleView, CommentViewSet, ShareView, NotificationViewSet

router = DefaultRouter()
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
    path("posts/<int:post_id>/like/", LikeToggleView.as_view(), name="post-like"),
    path("posts/<int:post_id>/share/", ShareView.as_view(), name="post-share"),
]
