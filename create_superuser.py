import os
import sys
import django

sys.path.insert(0, '/home/engine/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        password='admin123',
        email='admin@example.com'
    )
    print(f"Superuser created: {admin.username}")
else:
    print("Superuser already exists")
