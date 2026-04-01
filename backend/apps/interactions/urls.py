from django.urls import path

from apps.interactions.views import CommentListCreateView, LikeView, ShareView

urlpatterns = [
    path("likes/", LikeView.as_view(), name="interaction-like"),
    path("comments/", CommentListCreateView.as_view(), name="interaction-comments"),
    path("shares/", ShareView.as_view(), name="interaction-shares"),
]
