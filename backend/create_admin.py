import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
django.setup()

from apps.accounts.models import User

def create_admin():
    username = "admin"
    email = "admin@example.com"
    password = "1234567890"
    
    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser {username}...")
        User.objects.create_superuser(username=username, email=email, password=password)
        print("Superuser created successfully!")
    else:
        print(f"Superuser {username} already exists.")

if __name__ == "__main__":
    create_admin()
