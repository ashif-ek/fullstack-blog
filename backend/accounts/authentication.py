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

        # 3. Check Token Version
        token_version = validated_token.get("token_version")
        # If token has no version (old token) but user has version > 1, fail?
        # Or just check if present. Let's assume strict if field exists.

        # We need to fetch the user to check their version.
        # Efficiently we could do this via the session.user if select_related,
        # but session.user is a foreign key.
        # Optimized: `session = UserSession.objects.select_related('user').get(...)`
        # But `authenticate` returns (user, token). We usually fetch user at the end.

        # Let's get the user from the session object (DB hit).
        user = session.user

        if token_version is not None:
            if token_version != user.token_version:
                raise AuthenticationFailed(
                    "Token version mismatch. Please login again."
                )
        else:
            # Backward compatibility or strict?
            # If user.token_version > 1 and token has None, it's an old token.
            if user.token_version > 1:
                raise AuthenticationFailed("Token version invalid.")

        # 4. Update Last Used
        session.save(update_fields=["last_used_at"])

        # 4. Return user and token
        return self.get_user(validated_token), validated_token
