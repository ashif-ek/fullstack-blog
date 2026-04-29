from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.models import HistoricalRecords


class User(AbstractUser):
    """
    Custom User model for the blog application.
    Includes token versioning for forced logout.
    """
    token_version = models.IntegerField(default=0)
    
    # Database Versioning / History
    history = HistoricalRecords()

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    # Database Versioning / History
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.user.username}'s Profile"


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    device_id = models.CharField(max_length=255)
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.device_id}"
