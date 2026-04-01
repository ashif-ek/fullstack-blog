from __future__ import annotations

from rest_framework import serializers

from apps.interactions.models import Comment


class CommentCreateSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(min_value=1)
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    body = serializers.CharField(max_length=2000)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "post_id", "user_id", "parent_id", "depth", "body", "created_at")
        read_only_fields = fields


class LikeActionSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(min_value=1)


class ShareActionSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(min_value=1)
    channel = serializers.CharField(max_length=64, required=False, allow_blank=True)
