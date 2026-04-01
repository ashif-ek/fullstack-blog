from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.interactions.serializers import CommentCreateSerializer, LikeActionSerializer, ShareActionSerializer
from apps.interactions.services.comment_service import create_comment, list_comments_first_page
from apps.interactions.services.like_service import register_like
from apps.interactions.services.share_service import register_share


class LikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LikeActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = register_like(
            user_id=request.user.id,
            post_id=serializer.validated_data["post_id"],
        )
        if result.rate_limited:
            return Response({"detail": "Too many like attempts"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        return Response({"liked": result.liked, "count": result.count}, status=status.HTTP_200_OK)


class ShareView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ShareActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        register_share(
            user_id=request.user.id,
            post_id=serializer.validated_data["post_id"],
            channel=serializer.validated_data.get("channel", ""),
        )
        return Response({"status": "queued"}, status=status.HTTP_202_ACCEPTED)


class CommentListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            post_id = int(request.query_params.get("post_id", "0"))
        except ValueError:
            post_id = 0
        if post_id <= 0:
            return Response({"detail": "post_id query param is required"}, status=status.HTTP_400_BAD_REQUEST)
        comments = list_comments_first_page(post_id=post_id)
        return Response({"results": comments}, status=status.HTTP_200_OK)

    def post(self, request):
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
