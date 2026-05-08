from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from simple_history.models import HistoricalRecords


class Comment(models.Model):
    post_id = models.PositiveBigIntegerField(db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )
    depth = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(3)],
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Database Versioning / History
    history = HistoricalRecords()

    class Meta:
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if self.parent:
            self.depth = min(self.parent.depth + 1, 3)
        super().save(*args, **kwargs)


class PostLikeCounter(models.Model):
    post_id = models.PositiveBigIntegerField(unique=True, db_index=True)
    count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)


class UserPostLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    post_id = models.PositiveBigIntegerField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post_id")
        indexes = [
            models.Index(fields=["user", "post_id"]),
        ]


class NotificationDigest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_digests",
        null=True,
        blank=True,
    )
    payload = models.JSONField(default=dict)
    delivered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="actions"
    )
    verb = models.CharField(max_length=255) # e.g., "like", "comment", "share"
    target_id = models.PositiveBigIntegerField(null=True, blank=True)
    target_type = models.CharField(max_length=50, null=True, blank=True) # e.g., "post"
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor} {self.verb}ed something for {self.recipient}"
