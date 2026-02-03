from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from accounts.models import UserSession

User = get_user_model()


class SessionManagementTests(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "testpass123"
        self.user = User.objects.create_user(email=self.email, password=self.password)
        self.login_url = reverse("token_obtain_pair")
        self.profile_url = reverse("api_profile")
        self.logout_url = reverse("api_logout")
        self.logout_all_url = reverse("api_logout_all")
        self.sessions_url = reverse("session_list")
        self.change_password_url = reverse("change_password")

    def test_login_creates_session(self):
        response = self.client.post(
            self.login_url, {"email": self.email, "password": self.password}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        # Verify session created in DB
        self.assertEqual(UserSession.objects.count(), 1)
        session = UserSession.objects.first()
        self.assertEqual(session.user, self.user)
        self.assertTrue(session.is_active)

    def test_access_resource_with_session(self):
        # Login
        login_resp = self.client.post(
            self.login_url, {"email": self.email, "password": self.password}
        )
        access_token = login_resp.data["access"]

        # Access Profile
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_revokes_access(self):
        # Login
        login_resp = self.client.post(
            self.login_url, {"email": self.email, "password": self.password}
        )
        access_token = login_resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Logout
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify DB
        session = UserSession.objects.first()
        self.assertFalse(session.is_active)

        # Verify Access Denied
        response = self.client.get(self.profile_url)
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )  # Or 401 depending on config

    def test_logout_all(self):
        # Create 2 sessions (simulate by logging in twice)
        self.client.post(
            self.login_url, {"email": self.email, "password": self.password}
        )
        login_resp2 = self.client.post(
            self.login_url, {"email": self.email, "password": self.password}
        )
        access_token2 = login_resp2.data["access"]

        self.assertEqual(UserSession.objects.count(), 2)

        # Logout All
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token2}")
        response = self.client.post(self.logout_all_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check all sessions inactive
        self.assertFalse(UserSession.objects.filter(is_active=True).exists())

    def test_change_password_revokes_sessions(self):
        # Login
        login_resp = self.client.post(
            self.login_url, {"email": self.email, "password": self.password}
        )
        access_token = login_resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Change Password
        new_pass = "newpass456"
        response = self.client.put(
            self.change_password_url,
            {"old_password": self.password, "new_password": new_pass},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check user password updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_pass))

        # Check session revoked
        session = UserSession.objects.first()
        self.assertFalse(session.is_active)

        # Verify Access Denied
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_session_list(self):
        login_resp = self.client.post(
            self.login_url, {"email": self.email, "password": self.password}
        )
        access_token = login_resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.get(self.sessions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]["is_current"])
