import os
import django
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from accounts.forms import RegisterForm
from accounts.models import User

def verify_unified_auth():
    print("--- Verifying Unified Authentication (Web + JWT) ---")
    
    email = 'unified@example.com'
    password = 'unifiedpassword123'
    
    # 1. Cleanup
    User.objects.filter(email=email).delete()
    
    # 2. Web Registration
    print("\n1. Web Registration...")
    form = RegisterForm(data={'email': email, 'password': password})
    if form.is_valid():
        user = form.save()
        print(f"   Success: User {user.email} created via RegisterForm.")
        print(f"   Stored Password Hash: {user.password[:20]}...")
    else:
        print("   Failure: Form invalid", form.errors)
        return

    c = Client()

    # 3. Web Login
    print("\n2. Web Login...")
    response = c.post('/login/', {'email': email, 'password': password})
    if response.status_code == 302 and 'home' in response.url or response.url == '/':
        print("   Success: Web login redirected to home.")
    else:
        print(f"   Failure: Web login returned {response.status_code} {response.url if response.status_code==302 else ''}")

    # 4. JWT Login
    print("\n3. JWT Login...")
    from rest_framework.test import APIClient
    api_client = APIClient()
    response = api_client.post('/api/token/', {'email': email, 'password': password}, format='json')
    
    if response.status_code == 200:
        print("   Success: JWT Token obtained.")
        print(f"   Access Token: {response.data.get('access')[:20]}...")
    else:
        print(f"   Failure: JWT Login failed with {response.status_code}")
        print(response.data)

    # 5. Cleanup
    user.delete()
    print("\n--- Verification Complete ---")

if __name__ == '__main__':
    verify_unified_auth()
