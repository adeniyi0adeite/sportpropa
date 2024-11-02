from django.core.management.base import BaseCommand
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Send test email'

    def handle(self, *args, **kwargs):
        send_mail(
            'Subject Message',
            'This is test message',
            'info@sportpropa.com',
            ['kingskillash@gmail.com'],
            fail_silently=False,
        )
        self.stdout.write(self.style.SUCCESS('Email sent successfully'))
