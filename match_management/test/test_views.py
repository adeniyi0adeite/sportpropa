from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from competition_management.models import Competition, Team, Player, Coach, PlayerRegistration
from standing_management.models import Standing
from match_management.models import Match, Result, Goal, Card, Substitution, Save, Penalty

from ..views import aggregate_game_events_by_minute



class MatchManagementViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.coach = Coach.objects.create(name="John Doe", location="New York")
        self.team1 = Team.objects.create(name="Team 1", coach=self.coach, founded_year=1990)
        self.team2 = Team.objects.create(name="Team 2", coach=self.coach, founded_year=1992)
        self.user1 = User.objects.create_user(username='player1', password='12345')
        self.user2 = User.objects.create_user(username='player2', password='12345')
        self.player1 = Player.objects.create(name=self.user1, team=self.team1, position=Player.GOALKEEPER)
        self.player2 = Player.objects.create(name=self.user2, team=self.team2, position=Player.DEFENDER)
        self.competition = Competition.objects.create(
            name="Test Competition", start_date="2023-01-01", end_date="2023-12-31",
            organizer="Organizer", location="Location", description="Description",
            prize="Prize", competition_type=Competition.LEAGUE
        )
        self.match = Match.objects.create(
            competition=self.competition,
            home_team=self.team1,
            away_team=self.team2,
            match_date=timezone.now()
        )
        self.result = Result.objects.create(
            match=self.match, referee=None, stadium="Stadium", attendance=1000,
            home_team_score=2, away_team_score=1, added_time=3, completed=True
        )

        # Register players with their respective teams and the competition
        self.registration1 = PlayerRegistration.objects.create(player=self.player1, team=self.team1, competition=self.competition)
        self.registration2 = PlayerRegistration.objects.create(player=self.player2, team=self.team2, competition=self.competition)

    def test_matchresultdetails_view(self):
        # Create goals, cards, and other events
        goal1 = Goal.objects.create(match=self.match, scoring_team=self.team1, scorer=self.player1, assist=self.player2, minute=30)
        goal2 = Goal.objects.create(match=self.match, scoring_team=self.team1, scorer=self.player1, minute=60, is_own_goal=True)
        card = Card.objects.create(match=self.match, player=self.player1, card_type=Card.YELLOW, minute=70)
        substitution = Substitution.objects.create(match=self.match, team=self.team1, player_out=self.player1, player_in=self.player2, minute=80)
        save = Save.objects.create(match=self.match, goalkeeper=self.player1, minute=45)
        penalty = Penalty.objects.create(match=self.match, player=self.player1, minute=60, is_missed=False)

        response = self.client.get(reverse('matchresultdetails', args=[self.match.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.match.home_team.name)
        self.assertContains(response, self.match.away_team.name)
        self.assertContains(response, self.result.stadium)

        # Check for goals and events in the response context
        self.assertContains(response, goal1.scorer.name.get_full_name())
        self.assertContains(response, goal2.scorer.name.get_full_name())
        self.assertContains(response, 'Own Goal')
        self.assertContains(response, 'Yellow Card')
        self.assertContains(response, substitution.player_out.name.get_full_name())
        self.assertContains(response, save.goalkeeper.name.get_full_name())
        self.assertContains(response, 'Penalty scored')

    def test_aggregate_game_events_by_minute(self):
        goals = [
            Goal(match=self.match, scoring_team=self.team1, scorer=self.player1, assist=self.player2, minute=30),
            Goal(match=self.match, scoring_team=self.team1, scorer=self.player1, minute=60, is_own_goal=True)
        ]
        cards = [
            Card(match=self.match, player=self.player1, card_type=Card.YELLOW, minute=70),
            Card(match=self.match, player=self.player1, card_type=Card.RED, minute=75)
        ]
        substitutions = [
            Substitution(match=self.match, team=self.team1, player_out=self.player1, player_in=self.player2, minute=80)
        ]
        saves = [
            Save(match=self.match, goalkeeper=self.player1, minute=45)
        ]
        penalties = [
            Penalty(match=self.match, player=self.player1, minute=60, is_missed=False)
        ]

        events = aggregate_game_events_by_minute(goals, cards, substitutions, saves, penalties)
        self.assertEqual(len(events[30]), 1)
        self.assertEqual(len(events[60]), 2)  # Goal and Penalty
        self.assertEqual(len(events[70]), 1)
        self.assertEqual(len(events[75]), 1)
        self.assertEqual(len(events[80]), 1)
        self.assertEqual(len(events[45]), 1)

        self.assertEqual(events[60][0]['event'], 'Goal')
        self.assertEqual(events[60][1]['event'], 'Penalty')

