from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User, Profile


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If the frontend sends 'email', map it to 'username'
        self.fields[self.username_field] = serializers.CharField(required=False)
        self.fields['email'] = serializers.CharField(required=False)

    def validate(self, attrs):
        # Map 'email' to 'username' if 'username' is not provided
        if not attrs.get(self.username_field) and attrs.get('email'):
            attrs[self.username_field] = attrs.get('email')
        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'token_version')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('bio', 'image', 'location', 'birth_date')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')
        
        if not username and email:
            # Derive username from email if not provided
            username = email.split('@')[0]
            # Ensure uniqueness (simple approach for now)
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password']
        )
        return user
