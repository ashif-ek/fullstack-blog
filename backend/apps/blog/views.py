from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Post
from .serializers import PostSerializer, PostHistorySerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        """
        Custom action to retrieve the history of a specific post.
        """
        post = self.get_object()
        history = post.history.all()
        serializer = PostHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='revert')
    def revert(self, request, pk=None):
        """
        Custom action to revert a post to a specific history version.
        """
        post = self.get_object()
        history_id = request.data.get('history_id')
        if not history_id:
            return Response({"error": "history_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            historical_post = post.history.get(history_id=history_id)
            historical_post.instance.save() # This reverts the instance
            return Response({"status": "reverted successfully"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
