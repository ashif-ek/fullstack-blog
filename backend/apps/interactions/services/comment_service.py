from django_redis import get_redis_connection
from django.db import transaction, models
from django.core.cache import cache
from ..models import Comment
from blog.models import Post

class CommentService:
    """
    Hardened Comment service with Strong Consistency and cursor-based caching.
    """
    @staticmethod
    def _get_cache_key(post_id, cursor="first"):
        return f"post:{post_id}:comments_page_{cursor}"

    @classmethod
    def get_comments_for_post(cls, post_id, cursor=None):
        """
        Fetch comments using cursor-based logic and Redis caching.
        """
        cache_key = cls._get_cache_key(post_id, cursor or "first")
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data, True
            
        # DB Fetch with optimized query
        queryset = Comment.objects.filter(post_id=post_id, parent=None, is_deleted=False).select_related('author').prefetch_related('replies', 'replies__author', 'replies__replies')
        
        # Cursor-based pagination (using created_at as simple cursor)
        if cursor:
            queryset = queryset.filter(created_at__lt=cursor)
            
        # Fetching small page size for hot posts
        comments = list(queryset[:10])
        
        # Invert the comments to serializable data (simplified here)
        return comments, False

    @classmethod
    def create_comment(cls, post_id, author_id, content, parent_id=None):
        """
        Atomic write path for comments with denormalized updates.
        """
        with transaction.atomic():
            post = Post.objects.select_for_update().get(pk=post_id)
            
            parent = None
            depth = 1
            if parent_id:
                parent = Comment.objects.select_for_update().get(pk=parent_id)
                depth = parent.depth + 1
                if depth > 3:
                    raise ValueError("Max depth limit of 3 exceeded.")
            
            comment = Comment.objects.create(
                post=post,
                author_id=author_id,
                content=content,
                parent=parent,
                depth=depth
            )
            
            # Update reply count if this is a reply
            if parent:
                parent.reply_count = models.F('reply_count') + 1
                parent.save()
            
            # Invalidate Redis cache for this post
            cls.invalidate_cache(post_id)
            
            return comment

    @classmethod
    def invalidate_cache(cls, post_id):
        """
        Invalidates ALL comment pages for a hot post.
        """
        conn = get_redis_connection("default")
        keys = conn.keys(f"post:{post_id}:comments_page_*")
        if keys:
            conn.delete(*keys)
