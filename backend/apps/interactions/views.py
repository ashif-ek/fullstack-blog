from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.interactions.models import Notification, PostLikeCounter, Comment
from apps.interactions.serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    LikeActionSerializer,
    ShareActionSerializer,
    NotificationSerializer,
)
from apps.interactions.services.comment_service import create_comment, list_comments_first_page
from apps.interactions.services.like_service import register_like
from apps.interactions.services.share_service import register_share


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "marked as read"})


class LikeView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, post_id):
        from apps.interactions.models import PostLikeCounter, UserPostLike
        from infra.redis import get_redis_client, safe_redis_call
        
        redis_client = get_redis_client()
        count_key = f"likes:count:{post_id}"
        user_set_key = f"likes:set:{post_id}"
        
        # Try to get from Redis first
        count = safe_redis_call(redis_client.get, count_key, default=None)
        
        if count is not None:
            count = int(count)
            liked = False
            if request.user.is_authenticated:
                liked = bool(safe_redis_call(redis_client.sismember, user_set_key, request.user.id, default=False))
        else:
            # Fallback to DB
            counter, _ = PostLikeCounter.objects.get_or_create(post_id=post_id, defaults={"count": 0})
            count = counter.count
            liked = False
            if request.user.is_authenticated:
                liked = UserPostLike.objects.filter(user=request.user, post_id=post_id).exists()
        
        return Response({"liked": liked, "count": count}, status=status.HTTP_200_OK)

    def post(self, request, post_id):
        result = register_like(
            user_id=request.user.id,
            post_id=post_id,
        )
        if result.rate_limited:
            return Response({"detail": "Too many like attempts"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        return Response({"liked": result.liked, "count": result.count}, status=status.HTTP_200_OK)


class ShareView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        serializer = ShareActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        register_share(
            user_id=request.user.id,
            post_id=post_id,
            channel=serializer.validated_data.get("channel", ""),
        )
        return Response({"status": "queued"}, status=status.HTTP_202_ACCEPTED)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.request.query_params.get("post_id")
        queryset = Comment.objects.filter(parent__isnull=True)
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    @action(detail=False, methods=["get"])
    def post_comments(self, request):
        try:
            post_id = int(request.query_params.get("post_id", "0"))
        except ValueError:
            post_id = 0
        if post_id <= 0:
            return Response({"detail": "post_id query param is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Only fetch top-level comments
        comments = Comment.objects.filter(post_id=post_id, parent__isnull=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = create_comment(
            user_id=request.user.id if request.user.is_authenticated else None,
            post_id=serializer.validated_data["post_id"],
            body=serializer.validated_data["body"],
            parent_id=serializer.validated_data.get("parent_id"),
        )
        if result["status"] == "rate_limited":
            return Response({"detail": "Too many comment attempts"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        if result["status"] == "depth_exceeded":
            return Response({"detail": "Comment depth exceeded (max=3)"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result["comment"], status=status.HTTP_201_CREATED)
