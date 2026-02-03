from django.urls import path
from .views import (
    register_view,
    login_view,
    home_view,
    logout_view,
    RegisterAPIView,
    ProfileView,
    CustomTokenObtainPairView,
    SessionListView,
    APILogoutView,
    LogoutAllView,
)
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # Template URLs
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("", home_view, name="home"),
    path("logout/", logout_view, name="logout"),
    # API URLs
    path("api/register/", RegisterAPIView.as_view(), name="api_register"),
    path("api/profile/", ProfileView.as_view(), name="api_profile"),
    # Auth & Sessions
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/sessions/", SessionListView.as_view(), name="session_list"),
    path("api/logout/", APILogoutView.as_view(), name="api_logout"),  # Current device
    path(
        "api/logout-all/", LogoutAllView.as_view(), name="api_logout_all"
    ),  # All devices
]
