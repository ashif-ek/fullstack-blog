from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer, MyTokenObtainPairSerializer
from .models import Profile, User


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile
