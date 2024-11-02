from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import UserProfile, Post, Comment, Like
from competition_management.models import Player, Team
from django.core.files.uploadedfile import SimpleUploadedFile


class UserManagementTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user_profile = UserProfile.objects.create(user=self.user, bio='Test bio')
        self.team = Team.objects.create(name='Test Team')
        self.login_url = reverse('loginform')
        self.registration_url = reverse('registrationform')
        self.userprofile_url = reverse('userprofile', kwargs={'username': self.user.username})
        self.logout_url = reverse('logout')

    def test_login_view(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': '12345'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_registration_view(self):
        response = self.client.post(self.registration_url, {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password1': '12345test',
            'password2': '12345test',
            'date_of_birth': '2000-01-01',
            'bio': 'New user bio'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_userprofile_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.userprofile_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test bio')

    def test_logout_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

    def test_change_profile_picture(self):
        self.client.login(username='testuser', password='12345')
        picture = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('change_profile_picture', kwargs={'username': self.user.username}), {'new_picture': picture})
        self.assertEqual(response.status_code, 302)
        self.user_profile.refresh_from_db()
        self.assertIsNotNone(self.user_profile.picture)

    def test_create_post(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('create_post'), {
            'caption': 'Test caption',
            'image': SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.caption, 'Test caption')

    def test_edit_post(self):
        self.client.login(username='testuser', password='12345')
        post = Post.objects.create(author=self.user_profile, caption='Old caption')
        response = self.client.post(reverse('edit_post', kwargs={'post_id': post.id}), {'content': 'New caption'})
        self.assertEqual(response.status_code, 302)
        post.refresh_from_db()
        self.assertEqual(post.caption, 'New caption')

    def test_add_comment(self):
        self.client.login(username='testuser', password='12345')
        post = Post.objects.create(author=self.user_profile, caption='Test post')
        response = self.client.post(reverse('add_comment', kwargs={'post_id': post.id}), {
            'comment_text': 'Test comment',
            'redirect_to': reverse('post_detail', kwargs={'post_id': post.id})
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'Test comment')

    def test_delete_comment(self):
        self.client.login(username='testuser', password='12345')
        post = Post.objects.create(author=self.user_profile, caption='Test post')
        comment = Comment.objects.create(post=post, author=self.user_profile, content='Test comment')
        response = self.client.post(reverse('delete_comment', kwargs={'comment_id': comment.id}), {'post_owner_username': self.user.username})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 0)

    def test_toggle_like(self):
        self.client.login(username='testuser', password='12345')
        post = Post.objects.create(author=self.user_profile, caption='Test post')
        response = self.client.post(reverse('toggle_like', kwargs={'post_id': post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['liked'])
        self.assertEqual(Like.objects.count(), 1)
        response = self.client.post(reverse('toggle_like', kwargs={'post_id': post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['liked'])
        self.assertEqual(Like.objects.count(), 0)

    def test_follow_unfollow_user(self):
        self.client.login(username='testuser', password='12345')
        other_user = User.objects.create_user(username='otheruser', password='12345')
        other_user_profile = UserProfile.objects.create(user=other_user, bio='Other user bio')
        response = self.client.post(reverse('follow_unfollow_user', kwargs={'target_username': other_user.username}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user_profile.following.filter(id=other_user_profile.id).exists())
        response = self.client.post(reverse('follow_unfollow_user', kwargs={'target_username': other_user.username}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.user_profile.following.filter(id=other_user_profile.id).exists())
