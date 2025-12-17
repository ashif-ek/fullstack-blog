import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from accounts.models import User

def test_web_flow():
    email = 'webtest@example.com'
    password = 'webpassword123'
    
    # Cleanup
    User.objects.filter(email=email).delete()
    
    print("1. Registering user via Model directly (simulating successful register)...")
    # We use the form logic manually or just create user with hashed password
    from accounts.forms import RegisterForm
    # Actually, let's use the Form to be sure
    form_data = {'email': email, 'password': password}
    form = RegisterForm(data=form_data)
    if form.is_valid():
        form.save()
        print("   User registered successfully.")
    else:
        print("   Registration form invalid:", form.errors)
        return

    print("2. Logging in...")
    c = Client()
    login_url = '/login/'
    response = c.post(login_url, {'email': email, 'password': password})
    
    print(f"   Login Response Code: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirects to: {response.url}")
        if response.url == '/list' or response.url == '/' or 'home' in response.url: 
             # Note: 'home' url name usually maps to / or /home/
             pass
    else:
        print("   Login did not redirect.")
    
    # Check session
    session = c.session
    print(f"   Session user_id: {session.get('user_id')}")

    print("3. Accessing Home Page...")
    home_url = '/' # Assuming home is root
    response = c.get(home_url)
    print(f"   Home Response Code: {response.status_code}")
    if response.status_code == 302:
        print(f"   Home redirected to: {response.url}")
    elif response.status_code == 200:
        print("   Home page accessed successfully.")

if __name__ == '__main__':
    test_web_flow()
