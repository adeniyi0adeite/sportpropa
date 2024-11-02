from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from user_management.models import UserProfile
from fanbanter.models import FanBanterPost, FanBanterComment, FanBanterLike

class FanBanterViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user, bio='Test bio')
        self.client.login(username='testuser', password='12345')
        self.post = FanBanterPost.objects.create(title='Test Post', caption='Test Caption', category='SOCCER')

    def test_fanbanter_view(self):
        response = self.client.get(reverse('fanbanter', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_fanbanter_comment_view(self):
        response = self.client.post(reverse('fanbanter_comment', args=[self.post.id]), {
            'message': 'Test Comment',
            'redirect_to': 'fanbanter',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FanBanterComment.objects.count(), 1)
        comment = FanBanterComment.objects.first()
        self.assertEqual(comment.content, 'Test Comment')

    def test_delete_fanbanter_comment_view(self):
        comment = FanBanterComment.objects.create(post=self.post, author=self.profile, content='Test Comment')
        response = self.client.post(reverse('delete_fanbanter_comment', args=[comment.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FanBanterComment.objects.count(), 0)

    def test_toggle_fanbanter_like_view(self):
        response = self.client.post(reverse('toggle_fanbanter_like', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FanBanterLike.objects.count(), 1)
        like = FanBanterLike.objects.first()
        self.assertEqual(like.post, self.post)

        # Unlike the post
        response = self.client.post(reverse('toggle_fanbanter_like', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FanBanterLike.objects.count(), 0)
