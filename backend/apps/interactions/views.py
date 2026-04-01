from rest_framework import viewsets, status, views, pagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from blog.models import Post
from .models import Comment, Notification
from .serializers import CommentSerializer, NotificationSerializer
from .services.like_service import LikeService
from .services.comment_service import CommentService
from .services.notification_service import NotificationService
from .utils.rate_limit import RateLimiter

class CursorPagination(pagination.CursorPagination):
    page_size = 10
    ordering = "-created_at"

class LikeToggleView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        # 1. Rate Limiting
        RateLimiter.check_rate_limit(request.user.id, "like", limit=20, window=60)
        
        # 2. Toggle via Service (Idempotent WAL)
        result = LikeService.toggle_like(post_id, request.user.id)
        
        # 3. Buffer notification only if liked
        if result["is_liked"]:
            post = get_object_or_404(Post, pk=post_id)
            if post.author_id != request.user.id:
                NotificationService.buffer_notification(
                    post.author_id, request.user.id, 'like', post_id
                )
        
        return Response(result)

    def get(self, request, post_id):
        user_id = request.user.id if request.user.is_authenticated else None
        data = LikeService.get_status(post_id, user_id)
        return Response(data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CursorPagination

    def get_queryset(self):
        post_id = self.request.query_params.get('post_id')
        if post_id:
            return Comment.objects.filter(post_id=post_id, parent=None, is_deleted=False).select_related('author').prefetch_related('replies', 'replies__author')
        return Comment.objects.filter(author=self.request.user, is_deleted=False)

    def create(self, request, *args, **kwargs):
        # 1. Rate Limiting
        RateLimiter.check_rate_limit(request.user.id, "comment", limit=5, window=60)
        
        # 2. Write via Service (Strong Consistency)
        post_id = request.data.get('post')
        parent_id = request.data.get('parent')
        content = request.data.get('content')
        
        try:
            comment = CommentService.create_comment(
                post_id, request.user.id, content, parent_id
            )
            
            # 3. Buffer notification
            recipient_id = comment.parent.author_id if comment.parent else comment.post.author_id
            if recipient_id != request.user.id:
                NotificationService.buffer_notification(
                    recipient_id, request.user.id, 'comment', post_id
                )
                
            serializer = self.get_serializer(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def post_comments(self, request):
        post_id = request.query_params.get('post_id')
        cursor = request.query_params.get('cursor')
        
        if not post_id:
            return Response({"error": "post_id required"}, status=400)
            
        # 1. Page Caching (Service logic)
        data, was_cached = CommentService.get_comments_for_post(post_id, cursor)
        
        if was_cached:
            return Response(data, headers={"X-Cache": "HIT"})
            
        # 2. Serialize and return (Simplified here for length)
        # In prod, we'd use the queryset from CommentService and paginate it here
        queryset = Comment.objects.filter(post_id=post_id, parent=None, is_deleted=False).select_related('author').prefetch_related('replies', 'replies__author')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class ShareView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        # 1. Rate Limiting
        RateLimiter.check_rate_limit(request.user.id, "share", limit=10, window=60)
        
        # 2. Async Buffer Notification (Shared event is fully async)
        shared_to = request.data.get('shared_to', 'general')
        # Here we'd call a ShareService that buffers the share event for Celery
        # For brevity, we call a simplified buffer
        post = get_object_or_404(Post, pk=post_id)
        NotificationService.buffer_notification(
            post.author_id, request.user.id, 'share', post_id
        )
        return Response({"status": "share logged"}, status=status.HTTP_202_ACCEPTED)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "read"})
