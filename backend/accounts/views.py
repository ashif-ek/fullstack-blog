from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth.hashers import check_password
from .models import User, Profile, UserSession

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
)

# ------------------------------------------------------------------------------
# Template Views (MVC)
# ------------------------------------------------------------------------------


def register_view(request):
    """
    Handles new user signup. Shows the form on GET and saves the user on POST.
    Password hashing is done inside the form for safety.
    """
    form = RegisterForm()

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # safe because RegisterForm hashes the password
            return redirect("login")

    return render(request, "register.html", {"form": form})


def login_view(request):
    """
    Simple login view. Validates credentials and stores user ID in session.
    Compares the raw password with the hashed one for security.
    """
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = User.objects.filter(email=email).first()

            # check_password handles secure comparison with the hashed password
            if user and check_password(password, user.password):
                request.session["user_id"] = user.id
                return redirect("home")

    return render(request, "login.html", {"form": form})


def home_view(request):
    """
    Basic protected page. Only loads if the user has a valid session.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    return render(request, "home.html")


def logout_view(request):
    """
    Clears all session data to fully log the user out.
    """
    request.session.flush()
    return redirect("login")


# ------------------------------------------------------------------------------
# API Views (DRF)
# ------------------------------------------------------------------------------


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Create profile if it doesn't exist (signal alternative for simplicity)
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class SessionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None  # Manual serialization

    def get(self, request, *args, **kwargs):
        sessions = UserSession.objects.filter(user=request.user, is_active=True)
        data = []
        # Get current session ID from the token calling this API
        current_session_id = None
        if (
            request.auth
            and isinstance(request.auth, dict)
            and "session_id" in request.auth
        ):
            current_session_id = request.auth["session_id"]
        elif request.auth and hasattr(
            request.auth, "get"
        ):  # It might be a Token object wrapper?
            current_session_id = request.auth.get("session_id")

        # SimpleJWT returns a Token object which behaves like a dict but checking type is safe

        for s in sessions:
            data.append(
                {
                    "id": s.id,  # Internal DB ID
                    "device": s.user_agent,
                    "ip": s.ip_address,
                    "last_active": s.last_used_at,
                    "is_current": s.jti == current_session_id,
                }
            )
        return Response(data)


class APILogoutView(APIView):
    """
    Logout the DEVICE associated with the current token.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.auth.get("session_id")
        if session_id:
            UserSession.objects.filter(jti=session_id).update(is_active=False)
            return Response(
                {"detail": "Logged out successfully."}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "No session info found in token."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LogoutAllView(APIView):
    """
    Logout ALL devices for the user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        UserSession.objects.filter(user=request.user).update(is_active=False)
        return Response({"detail": "All sessions revoked."}, status=status.HTTP_200_OK)


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password that also revokes all sessions.
    """

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.token_version += 1
            self.object.save()

            # Revoke all sessions
            UserSession.objects.filter(user=self.object).update(is_active=False)

            return Response(
                {"detail": "Password updated successfully. Please log in again."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
