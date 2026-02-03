from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Profile, UserSession


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Profile
        fields = ["id", "email", "full_name", "bio", "institution", "image"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"], password=validated_data["password"]
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # 'self.user' is populated by super().validate()

        # Generate our own refresh token object to ensure we have control
        # (This duplicates work slightly but ensures we get the exact JTI we want)
        refresh = self.get_token(self.user)

        request = self.context.get("request")
        user_agent = request.META.get("HTTP_USER_AGENT", "")[:255]
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        # Create session using the Refresh Token's JTI as the key
        session_jti = refresh["jti"]

        UserSession.objects.create(
            user=self.user, jti=session_jti, user_agent=user_agent, ip_address=ip
        )

        # Embed 'session_id' into the tokens
        refresh["session_id"] = session_jti

        # Handle access token
        access = refresh.access_token
        access["session_id"] = session_jti

        # Update return data
        data["refresh"] = str(refresh)
        data["access"] = str(access)

        return data
