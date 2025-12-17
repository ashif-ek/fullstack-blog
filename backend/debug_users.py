import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import User as AccountUser

def check_users():
    AuthUser = get_user_model()
    
    print(f"Standard Auth User Model: {AuthUser}")
    print(f"Standard Auth Users Count: {AuthUser.objects.count()}")
    
    print(f"Custom AccountUser Model: {AccountUser}")
    print(f"Custom Account Users Count: {AccountUser.objects.count()}")

    # List emails in AccountUser to see if the user's registration worked
    print("\nAccountUser Emails:")
    for u in AccountUser.objects.all():
        print(f" - {u.email} (ID: {u.id})")

if __name__ == '__main__':
    check_users()
