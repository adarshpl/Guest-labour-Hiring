"""
Run this script once to set up the database and create the Admin account.
Usage: python setup.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guest_labour_hiring.settings')
django.setup()

from django.contrib.auth.models import User
from hiring.models import UserProfile

# Create superuser / Admin account
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_user(username='admin', password='admin123', is_staff=True, is_superuser=True)
    UserProfile.objects.create(user=u, user_type='Admin', status='Active')
    print("✅ Admin account created → username: admin | password: admin123")
else:
    print("ℹ️  Admin account already exists.")

# Create a Police account for testing
if not User.objects.filter(username='police1').exists():
    u = User.objects.create_user(username='police1', password='police123')
    UserProfile.objects.create(user=u, user_type='Police', status='Active')
    print("✅ Police account created → username: police1 | password: police123")

print("\nSetup complete! Run: python manage.py runserver")
