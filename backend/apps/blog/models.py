from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex
from simple_history.models import HistoricalRecords

User = get_user_model()


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0, db_index=True)

    # Soft Delete Fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Postgres Full Text Search
    search_vector = SearchVectorField(null=True, blank=True)

    # Database Versioning / History
    history = HistoricalRecords()

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Access to all including deleted

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"]),
        ]

    def save(self, *args, **kwargs):
        # Save first to get an ID if creating
        super().save(*args, **kwargs)
        # Update the search vector directly in DB without triggering save again
        if self.title and self.content:
            Post.objects.filter(pk=self.pk).update(
                search_vector=SearchVector("title", weight="A")
                + SearchVector("content", weight="B")
            )

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        super().save()  # don't trigger recursive update from normal save()

    def __str__(self):
        return self.title
