from django.test import TestCase
from django.contrib.auth.models import User
from user_management.models import UserProfile
from fanbanter.models import FanBanterPost, FanBanterComment, FanBanterLike

class FanBanterModelsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user, bio='Test bio')
        self.post = FanBanterPost.objects.create(title='Test Post', caption='Test Caption', category='SOCCER')

    def test_fanbanterpost_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.caption, 'Test Caption')
        self.assertEqual(self.post.category, 'SOCCER')

    def test_fanbantercomment_creation(self):
        comment = FanBanterComment.objects.create(post=self.post, author=self.profile, content='Test Comment')
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.profile)
        self.assertEqual(comment.content, 'Test Comment')

    def test_fanbanterlike_creation(self):
        like = FanBanterLike.objects.create(post=self.post, user=self.profile)
        self.assertEqual(like.post, self.post)
        self.assertEqual(like.user, self.profile)

    def test_fanbantercomment_reply(self):
        comment = FanBanterComment.objects.create(post=self.post, author=self.profile, content='Test Comment')
        reply = FanBanterComment.objects.create(post=self.post, author=self.profile, content='Test Reply', parent=comment)
        self.assertEqual(reply.parent, comment)
        self.assertEqual(reply.content, 'Test Reply')
 