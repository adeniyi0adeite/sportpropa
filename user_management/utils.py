import os
import django
from django.core.mail import send_mail

# Set the settings module for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportbase.settings')  # Make sure to use the correct path to your settings file

# Initialize Django
django.setup()

def send_email(subject, message, recipient):
    send_mail(
        subject,
        message,
        'info@sportpropa.com',  # Use your domain's email address
        [recipient],
        fail_silently=False,
    )

