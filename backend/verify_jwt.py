import os
import django
import sys

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

def verify_jwt():
    User = get_user_model()
    username = 'testuser_jwt_verify'
    password = 'testpassword123'
    email = 'test_verify@example.com'

    # Clean up any existing user
    try:
        user = User.objects.get(username=username)
        print(f"Deleting existing user {username}")
        user.delete()
    except User.DoesNotExist:
        pass

    # Create user
    print(f"Creating user {username}...")
    user = User.objects.create_user(username=username, password=password, email=email)

    client = APIClient()
    
    # Test Token Obtain
    url = '/api/token/'
    print(f"Testing POST {url}...")
    data = {
        'username': username,
        'password': password
    }

    response = client.post(url, data, format='json')

    print(f"Response Status Code: {response.status_code}")
    if hasattr(response, 'data'):
        print("Response has .data attribute")
    else:
        print("Response DOES NOT have .data attribute")
        print(f"Response Content: {response.content}")

    if response.status_code == 200:
        print("SUCCESS: Token obtained successfully.")
        print(f"Access Token: {response.data.get('access')[:20]}...")
        print(f"Refresh Token: {response.data.get('refresh')[:20]}...")
        
        refresh_token = response.data.get('refresh')
        
        # Test Token Refresh
        refresh_url = '/api/token/refresh/'
        print(f"Testing POST {refresh_url}...")
        refresh_data = {'refresh': refresh_token}
        refresh_response = client.post(refresh_url, refresh_data, format='json')
        
        if refresh_response.status_code == 200:
             print("SUCCESS: Token refreshed successfully.")
             print(f"New Access Token: {refresh_response.data.get('access')[:20]}...")
        else:
             print(f"FAILURE: Refresh failed. Status {refresh_response.status_code}")
             print(refresh_response.data)

    else:
        print(f"FAILURE: Status {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Response Data: {response.data}")
        else:
            try:
                import json
                print(f"Response JSON: {response.json()}")
            except:
                with open('debug_response.html', 'wb') as f:
                    f.write(response.content)
                print("Saved response to debug_response.html")
        
    # Cleanup
    user.delete()
    print("Test user deleted.")

if __name__ == '__main__':
    verify_jwt()
