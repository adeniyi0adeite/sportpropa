from django.test import TestCase
from django.contrib.auth.models import User
from ..models import (
    Coach, Team, Competition, CupGroup, Player, PlayerRegistration, PlayerPost, Referee,
    TeamComment, TeamLike, CompetitionComment, CompetitionLike, PlayerComment, PlayerLike
)
from user_management.models import UserProfile
from standing_management.models import Standing

class CompetitionManagementTests(TestCase):

    def setUp(self):
        # Set up test data for models
        self.coach = Coach.objects.create(name="John Doe", location="New York")
        self.team = Team.objects.create(name="Test Team", coach=self.coach, founded_year=1990)
        self.user = User.objects.create_user(username='testplayer', password='12345')
        self.user_profile = UserProfile.objects.create(user=self.user, bio="Test Bio")
        self.player = Player.objects.create(name=self.user, team=self.team, position=Player.GOALKEEPER)
        self.competition = Competition.objects.create(
            name="Test Competition",
            organizer="Organizer", location="Location", description="Description",
            prize="Prize", competition_type=Competition.LEAGUE
        )

    def test_coach_creation(self):
        self.assertEqual(self.coach.name, "John Doe")
        self.assertEqual(self.coach.location, "New York")

    def test_team_creation(self):
        self.assertEqual(self.team.name, "Test Team")
        self.assertEqual(self.team.coach, self.coach)
        self.assertEqual(self.team.founded_year, 1990)

    def test_competition_creation(self):
        self.assertEqual(self.competition.name, "Test Competition")
        self.assertEqual(self.competition.organizer, "Organizer")
        self.assertEqual(self.competition.prize, "Prize")

    def test_cupgroup_creation(self):
        cup_competition = Competition.objects.create(
            name="Cup Competition",
            organizer="Organizer", location="Location", description="Description",
            prize="Prize", competition_type=Competition.CUP
        )
        cup_group = CupGroup.objects.create(name="Group A", competition=cup_competition)
        cup_group.teams.add(self.team)
        self.assertEqual(cup_group.name, "Group A")
        self.assertEqual(cup_group.competition, cup_competition)
        self.assertIn(self.team, cup_group.teams.all())

    def test_player_creation(self):
        self.assertEqual(self.player.name, self.user)
        self.assertEqual(self.player.team, self.team)
        self.assertEqual(self.player.position, Player.GOALKEEPER)

    def test_player_registration(self):
        player_registration = PlayerRegistration.objects.create(player=self.player, team=self.team, competition=self.competition,)
        self.assertEqual(player_registration.player, self.player)
        self.assertEqual(player_registration.team, self.team)
        self.assertEqual(player_registration.competition, self.competition)
        

    def test_player_post_creation(self):
        player_post = PlayerPost.objects.create(player=self.player, image='path/to/image.jpg')
        self.assertEqual(player_post.player, self.player)
        self.assertEqual(player_post.image, 'path/to/image.jpg')

    def test_referee_creation(self):
        referee = Referee.objects.create(name="Referee Name", country="Country", birth_date="1980-01-01")
        self.assertEqual(referee.name, "Referee Name")
        self.assertEqual(referee.country, "Country")
        self.assertEqual(referee.birth_date, "1980-01-01")

    def test_player_delete(self):
        self.player.delete()
        self.assertFalse(User.objects.filter(username='testplayer').exists())

    def test_cupgroup_standing_creation(self):
        cup_competition = Competition.objects.create(
            name="Cup Competition",
            organizer="Organizer", location="Location", description="Description",
            prize="Prize", competition_type=Competition.CUP
        )
        cup_group = CupGroup.objects.create(name="Group B", competition=cup_competition)
        cup_group.teams.add(self.team)
        cup_group.save()  # Save to trigger standings creation

        standings = Standing.objects.filter(competition=cup_competition, group=cup_group, team=self.team)
        self.assertEqual(standings.count(), 1)
        self.assertEqual(standings.first().points, 0)

    def test_team_comment_creation(self):
        team_comment = TeamComment.objects.create(team=self.team, author=self.user_profile, content="Great team!")
        self.assertEqual(team_comment.team, self.team)
        self.assertEqual(team_comment.author, self.user_profile)
        self.assertEqual(team_comment.content, "Great team!")

    def test_team_like_creation(self):
        team_comment = TeamComment.objects.create(team=self.team, author=self.user_profile, content="Great team!")
        team_like = TeamLike.objects.create(team=self.team, user=self.user_profile, comment=team_comment)
        self.assertEqual(team_like.team, self.team)
        self.assertEqual(team_like.user, self.user_profile)
        self.assertEqual(team_like.comment, team_comment)

    def test_competition_comment_creation(self):
        competition_comment = CompetitionComment.objects.create(competition=self.competition, author=self.user_profile, content="Exciting competition!")
        self.assertEqual(competition_comment.competition, self.competition)
        self.assertEqual(competition_comment.author, self.user_profile)
        self.assertEqual(competition_comment.content, "Exciting competition!")

    def test_competition_like_creation(self):
        competition_comment = CompetitionComment.objects.create(competition=self.competition, author=self.user_profile, content="Exciting competition!")
        competition_like = CompetitionLike.objects.create(competition=self.competition, user=self.user_profile, comment=competition_comment)
        self.assertEqual(competition_like.competition, self.competition)
        self.assertEqual(competition_like.user, self.user_profile)
        self.assertEqual(competition_like.comment, competition_comment)

    def test_player_comment_creation(self):
        player_comment = PlayerComment.objects.create(player=self.player, author=self.user_profile, content="Great player!")
        self.assertEqual(player_comment.player, self.player)
        self.assertEqual(player_comment.author, self.user_profile)
        self.assertEqual(player_comment.content, "Great player!")

    def test_player_like_creation(self):
        player_comment = PlayerComment.objects.create(player=self.player, author=self.user_profile, content="Great player!")
        player_like = PlayerLike.objects.create(player=self.player, user=self.user_profile, comment=player_comment)
        self.assertEqual(player_like.player, self.player)
        self.assertEqual(player_like.user, self.user_profile)
        self.assertEqual(player_like.comment, player_comment)
