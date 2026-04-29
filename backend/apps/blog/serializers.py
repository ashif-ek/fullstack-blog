from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'image', 'author', 'author_name',
            'created_at', 'updated_at', 'views', 'likes_count', 'is_deleted'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at', 'views', 'likes_count']


class PostHistorySerializer(serializers.Serializer):
    """
    Serializer for HistoricalRecords of Post.
    """
    history_id = serializers.IntegerField()
    history_date = serializers.DateTimeField()
    history_change_reason = serializers.CharField()
    history_type = serializers.CharField()
    history_user_id = serializers.IntegerField()
    
    # Model fields at the time of history record
    title = serializers.CharField()
    content = serializers.CharField()
    updated_at = serializers.DateTimeField()
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Map history types to human readable strings
        type_map = {'+': 'created', '~': 'updated', '-': 'deleted'}
        ret['change_type'] = type_map.get(instance.history_type, instance.history_type)
        return ret
