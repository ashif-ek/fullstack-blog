from rest_framework import serializers
from .models import Comment, Notification, Like
from django.contrib.auth import get_user_model

User = get_user_model()

class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email")

class CommentSerializer(serializers.ModelSerializer):
    author = UserMinimalSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "post", "author", "parent", "content", "created_at", "replies")
        read_only_fields = ("author", "created_at")

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class LikeDataSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
    count = serializers.IntegerField()
    is_liked = serializers.BooleanField()


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ("id", "actor", "verb", "target_post", "is_read", "created_at")
        read_only_fields = ("id", "actor", "verb", "target_post", "created_at")
