from rest_framework import viewsets, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from blog.models import Post
from .models import Comment, Notification
from .serializers import CommentSerializer, NotificationSerializer
from .services import LikeService, CommentService
from .tasks import send_interaction_notification, process_share_event


class LikeToggleView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        user_id = request.user.id
        post = get_object_or_404(Post, pk=post_id)
        
        # Check if already liked in Redis
        data = LikeService.get_likes_data(post_id, user_id)
        
        if data["is_liked"]:
            # Unlike
            LikeService.remove_like(post_id, user_id)
        else:
            # Like
            LikeService.add_like(post_id, user_id)
            # Async notification (don't notify self)
            if post.author_id != user_id:
                send_interaction_notification.delay(post.author_id, user_id, 'like', post_id)
        
        # Get updated stats
        updated_data = LikeService.get_likes_data(post_id, user_id)
        return Response(updated_data)

    def get(self, request, post_id):
        user_id = request.user.id if request.user.is_authenticated else None
        data = LikeService.get_likes_data(post_id, user_id)
        return Response(data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.request.query_params.get('post_id')
        if post_id:
            return Comment.objects.filter(post_id=post_id, parent=None, is_deleted=False)
        return Comment.objects.filter(author=self.request.user, is_deleted=False)

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        # Trigger notification to post author or parent comment author
        post = comment.post
        if comment.parent:
            recipient_id = comment.parent.author_id
        else:
            recipient_id = post.author_id
            
        if recipient_id != self.request.user.id:
            send_interaction_notification.delay(recipient_id, self.request.user.id, 'comment', post.id)
            
        # Invalidate/Update Cache for this post
        # Real-world: only cache 'hot' posts
        self._refresh_comment_cache(post.id)

    def _refresh_comment_cache(self, post_id):
        # Fetch top level comments and cache them
        comments = Comment.objects.filter(post_id=post_id, parent=None, is_deleted=False)[:10]
        data = CommentSerializer(comments, many=True).data
        CommentService.cache_hot_comments(post_id, data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def post_comments(self, request):
        post_id = request.query_params.get('post_id')
        if not post_id:
            return Response({"error": "post_id required"}, status=400)
            
        # Try Cache first
        cached = CommentService.get_cached_comments(post_id)
        if cached:
            return Response(cached)
            
        # Fallback to DB
        comments = Comment.objects.filter(post_id=post_id, parent=None, is_deleted=False)
        serializer = self.get_serializer(comments, many=True)
        # Populate cache
        CommentService.cache_hot_comments(post_id, serializer.data)
        return Response(serializer.data)


class ShareView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        shared_to = request.data.get('shared_to', 'general')
        # Offload to worker
        process_share_event.delay(post_id, request.user.id, shared_to)
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
