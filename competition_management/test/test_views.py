from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from competition_management.models import (
    Coach, Competition, CupGroup, Team, Player, PlayerRegistration, PlayerPost
)
from match_management.models import Result, Match, Goal, Save, Card
from standing_management.models import Standing
from myapp.models import Award  # Make sure this import is correct

class CompetitionManagementViewsTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.coach = Coach.objects.create(name="John Doe", location="New York")
        self.team = Team.objects.create(name="Test Team", coach=self.coach, founded_year=1990)
        self.player = Player.objects.create(name=self.user, team=self.team, position=Player.GOALKEEPER)
        self.competition = Competition.objects.create(
            name="Test Competition", start_date="2023-01-01", end_date="2023-12-31",
            organizer="Organizer", location="Location", description="Description",
            prize="Prize", competition_type=Competition.LEAGUE
        )
        self.award = Award.objects.create(
            player=self.player,
            date_awarded="2023-12-31",
            competition=self.competition,
            category=Award.PLAYER,
            player_award=Award.BEST_PLAYER
        )

    def test_player_view(self):
        response = self.client.get(reverse('player', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.name.get_full_name())

    def test_change_player_picture(self):
        picture = SimpleUploadedFile("new_picture.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('change_player_picture', args=[self.user.username]), {'new_picture': picture})
        self.assertEqual(response.status_code, 302)
        self.player.refresh_from_db()
        self.assertIsNotNone(self.player.picture)

    def test_upload_player_image(self):
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('upload_player_image', args=[self.player.id]), {'image': image})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PlayerPost.objects.count(), 1)

    def test_load_more_images(self):
        PlayerPost.objects.create(player=self.player, image='path/to/image1.jpg')
        PlayerPost.objects.create(player=self.player, image='path/to/image2.jpg')
        response = self.client.get(reverse('load_more_images', args=[self.player.id]), {'offset': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['images']), 2)

    def test_competition_view(self):
        response = self.client.get(reverse('competition', args=[self.competition.name]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.competition.name)

    def test_team_view(self):
        response = self.client.get(reverse('team', args=[self.team.name]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.team.name)
