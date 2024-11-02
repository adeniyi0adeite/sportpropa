from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator


import os
# Create your models here.



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True)  # Add this line
    picture = models.ImageField(upload_to='profile_pic/', blank=True, null=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    favorite_team = models.ForeignKey('competition_management.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='fans')
    bio = models.TextField(null=True, blank=True)

    def is_followed_by(self, user):
        return self.followers.filter(id=user.profile.id).exists()

    def __str__(self):
        return self.user.username
    

class Post(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    video = models.FileField(upload_to='post_videos/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov'])])

    def __str__(self):
        return f"Post by {self.author} on {self.created_at}"

    def delete(self, *args, **kwargs):
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        if self.video and os.path.isfile(self.video.path):
            os.remove(self.video.path)
        super().delete(*args, **kwargs)




class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"Comment by {self.author} on {self.post.author} post"
    
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user}"
