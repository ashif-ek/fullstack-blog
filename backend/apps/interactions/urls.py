from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.interactions.views import LikeView, ShareView, NotificationViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path("posts/<int:post_id>/like/", LikeView.as_view(), name="interaction-like"),
    path("posts/<int:post_id>/share/", ShareView.as_view(), name="interaction-share"),
]
