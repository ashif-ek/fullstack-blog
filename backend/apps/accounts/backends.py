from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Check if 'username' passed is actually an email
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Should not happen with unique email/username, but handle just in case
            return User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).first()

        if user.check_password(password):
            return user
        return None
