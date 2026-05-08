from __future__ import annotations

from rest_framework import serializers

from apps.interactions.models import Comment, Notification
from apps.accounts.serializers import UserSerializer


class CommentCreateSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(required=False)
    post = serializers.IntegerField(required=False)
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    parent = serializers.IntegerField(required=False, allow_null=True)
    body = serializers.CharField(required=False)
    content = serializers.CharField(required=False)

    def validate(self, attrs):
        # Map frontend 'post' to 'post_id'
        if 'post' in attrs and 'post_id' not in attrs:
            attrs['post_id'] = attrs.pop('post')
        
        # Map frontend 'content' to 'body'
        if 'content' in attrs and 'body' not in attrs:
            attrs['body'] = attrs.pop('content')

        # Map frontend 'parent' to 'parent_id'
        if 'parent' in attrs and 'parent_id' not in attrs:
            attrs['parent_id'] = attrs.pop('parent')

        if not attrs.get('post_id'):
            raise serializers.ValidationError("post_id or post is required")
        if not attrs.get('body'):
            raise serializers.ValidationError("body or content is required")
            
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(source='user', read_only=True)
    content = serializers.CharField(source='body', read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ("id", "post_id", "author", "parent_id", "depth", "content", "replies", "created_at")
        read_only_fields = fields

    def get_replies(self, obj):
        # Only get immediate children to avoid deep recursion if not handled by service
        if obj.depth < 3: # Assuming max depth is 3 as per model
            return CommentSerializer(obj.children.all(), many=True).data
        return []


class LikeActionSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(min_value=1)


class ShareActionSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(min_value=1)
    channel = serializers.CharField(max_length=64, required=False, allow_blank=True)


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ("id", "actor", "verb", "target_id", "target_type", "is_read", "created_at")
