from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from myapp.models import Post  # Import your Post model



class Command(BaseCommand):
    help = 'Deletes posts that are older than 72 hours'

    def handle(self, *args, **options):
        try:
            # Calculate the time 72 hours ago from now
            threshold_time = timezone.now() - timedelta(hours=72)

            # Filter posts older than 72 hours
            old_posts = Post.objects.filter(created_at__lt=threshold_time)

            # Count the posts for logging
            old_posts_count = old_posts.count()

            # Delete the old posts
            old_posts.delete()

            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {old_posts_count} posts older than 72 hours.'))
        except Exception as e:
            raise CommandError(f'Error deleting posts: {e}')
