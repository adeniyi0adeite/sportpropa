from django.db import models

from user_management.models import UserProfile

# Create your models here.




# BANTER SCHEMA
    
class FanBanterPost(models.Model):
    CATEGORY_CHOICES = [
        ('COMPETITION', 'Competition'),
        ('TEAM', 'Team'),
        ('PLAYER', 'Player'),
        ('SOCCER', 'Soccer'),
    ]

    title = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='fanbanterpost_images/', null=True, blank=True)
    caption = models.TextField(blank=True, null=True)
    details = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='GENERAL')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title or "FanBanter Post"


class FanBanterComment(models.Model):
    post = models.ForeignKey(FanBanterPost, on_delete=models.CASCADE, related_name='fanbanter_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='fanbanter_replies', null=True, blank=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"Comment by {self.author}"
    
class FanBanterLike(models.Model):
    post = models.ForeignKey(FanBanterPost, on_delete=models.CASCADE, null=True, blank=True, related_name='fanbanter_likes')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    comment = models.ForeignKey(FanBanterComment, on_delete=models.CASCADE, null=True, blank=True, related_name='fanbanter_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user}"