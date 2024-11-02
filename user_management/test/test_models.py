
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import UserProfile, Post, Comment, Like
import os

from competition_management.models import Team



class UserProfileTest(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        
        # Create UserProfile instances
        self.profile1 = UserProfile.objects.create(user=self.user1, bio="This is user1's bio")
        self.profile2 = UserProfile.objects.create(user=self.user2, bio="This is user2's bio")
        
        # Create a Team instance
        self.team = Team.objects.create(name='Test Team')

    def test_userprofile_creation(self):
        self.assertEqual(self.profile1.user.username, 'user1')
        self.assertEqual(self.profile1.bio, "This is user1's bio")
        self.assertIsNone(self.profile1.favorite_team)
        self.assertEqual(self.profile2.user.username, 'user2')
        self.assertEqual(self.profile2.bio, "This is user2's bio")

    def test_userprofile_str_method(self):
        self.assertEqual(str(self.profile1), 'user1')
        self.assertEqual(str(self.profile2), 'user2')

    def test_following_relationship(self):
        # User1 follows User2
        self.profile1.following.add(self.profile2)
        self.assertTrue(self.profile1.following.filter(id=self.profile2.id).exists())
        self.assertTrue(self.profile2.followers.filter(id=self.profile1.id).exists())

    def test_is_followed_by_method(self):
        self.profile1.following.add(self.profile2)
        self.assertTrue(self.profile2.is_followed_by(self.user1))
        self.assertFalse(self.profile1.is_followed_by(self.user2))

    def test_favorite_team(self):
        # Assign favorite team to profile1
        self.profile1.favorite_team = self.team
        self.profile1.save()
        self.assertEqual(self.profile1.favorite_team.name, 'Test Team')



class PostModelTest(TestCase):

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.profile1 = UserProfile.objects.create(user=self.user1, bio='This is user1 bio')

        # Create a test image file
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=open(os.path.join(os.path.dirname(__file__), 'test_image.jpg'), 'rb').read(),
            content_type='image/jpeg'
        )

        # Create a Post instance
        self.post = Post.objects.create(
            author=self.profile1,
            caption='Test caption',
            image=self.test_image
        )

    def test_post_creation(self):
        # Ensure Post instance is created correctly
        self.assertIsInstance(self.post, Post)
        self.assertEqual(self.post.author, self.profile1)
        self.assertEqual(self.post.caption, 'Test caption')
        self.assertTrue(self.post.image)

    def test_post_str(self):
        # Test the __str__ method
        self.assertEqual(str(self.post), f"Post by {self.profile1} on {self.post.created_at}")

    def test_post_delete(self):
        # Test the custom delete method
        self.post.delete()
        self.assertFalse(os.path.exists(self.post.image.path))



class CommentModelTest(TestCase):

    def setUp(self):
        # Create test users and profiles
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.profile1 = UserProfile.objects.create(user=self.user1, bio='This is user1 bio')
        self.profile2 = UserProfile.objects.create(user=self.user2, bio='This is user2 bio')

        # Create a test post
        self.post = Post.objects.create(
            author=self.profile1,
            caption='Test post caption'
        )

        # Create a test comment
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.profile2,
            content='This is a test comment'
        )

    def test_comment_creation(self):
        # Ensure Comment instance is created correctly
        self.assertIsInstance(self.comment, Comment)
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.author, self.profile2)
        self.assertEqual(self.comment.content, 'This is a test comment')

    def test_comment_str(self):
        # Test the __str__ method
        self.assertEqual(str(self.comment), f"Comment by {self.profile2} on {self.post.author} post")


class LikeModelTest(TestCase):

    def setUp(self):
        # Create test users and profiles
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.profile1 = UserProfile.objects.create(user=self.user1, bio='This is user1 bio')
        self.profile2 = UserProfile.objects.create(user=self.user2, bio='This is user2 bio')

        # Create a test post
        self.post = Post.objects.create(
            author=self.profile1,
            caption='Test post caption'
        )

        # Create a test comment
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.profile2,
            content='This is a test comment'
        )

        # Create a test like for post
        self.like_post = Like.objects.create(
            post=self.post,
            user=self.user2
        )

        # Create a test like for comment
        self.like_comment = Like.objects.create(
            comment=self.comment,
            user=self.user1
        )

    def test_like_post_creation(self):
        # Ensure Like instance for post is created correctly
        self.assertIsInstance(self.like_post, Like)
        self.assertEqual(self.like_post.post, self.post)
        self.assertEqual(self.like_post.user, self.user2)
        self.assertIsNone(self.like_post.comment)

    def test_like_comment_creation(self):
        # Ensure Like instance for comment is created correctly
        self.assertIsInstance(self.like_comment, Like)
        self.assertEqual(self.like_comment.comment, self.comment)
        self.assertEqual(self.like_comment.user, self.user1)
        self.assertIsNone(self.like_comment.post)

    def test_like_str(self):
        # Test the __str__ method
        self.assertEqual(str(self.like_post), f"Like by {self.user2}")
        self.assertEqual(str(self.like_comment), f"Like by {self.user1}")





