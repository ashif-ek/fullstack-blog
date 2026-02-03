from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from .models import UserSession


class SessionJWTAuthentication(JWTAuthentication):
    """
    Extends JWTAuthentication to verify that the token's 'session_id' corresponds
    to an active UserSession.
    """

    def authenticate(self, request):
        # 1. Standard JWT validation
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        # 2. Check Session Validity
        # We expect a 'session_id' claim which matches the UserSession.jti
        session_id = validated_token.get("session_id")
        user_id = validated_token.get("user_id")

        if not session_id:
            # Fallback: if no session_id, maybe strictly fail?
            # Or allow if configured? For now, STRICT.
            raise InvalidToken("Token has no 'session_id' claim.")

        try:
            session = UserSession.objects.get(jti=session_id, user_id=user_id)
        except UserSession.DoesNotExist:
            raise AuthenticationFailed("Session does not exist or has been revoked.")

        if not session.is_active:
            raise AuthenticationFailed("Session is inactive.")

        # 3. Update Last Used
        session.save(update_fields=["last_used_at"])

        # 4. Return user and token
        return self.get_user(validated_token), validated_token
