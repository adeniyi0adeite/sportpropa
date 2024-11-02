from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from competition_management.models import Competition, CupGroup, Team, Player, Coach, Referee, PlayerRegistration
from standing_management.models import Standing
from match_management.models import (
    Match, Result, MatchStatistic, Save, Goal, Penalty, Foul, Card, Substitution, Injury
)

class MatchManagementModelsTest(TestCase):

    def setUp(self):
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
        self.group = CupGroup.objects.create(name="Group A", competition=self.competition)
        self.match = Match.objects.create(
            competition=self.competition, group=self.group,
            home_team=self.team1, away_team=self.team2, match_date=timezone.now()
        )
        self.referee = Referee.objects.create(name="Referee 1", country="Country", birth_date="1980-01-01")
        self.result = Result.objects.create(
            match=self.match, referee=self.referee, stadium="Stadium", attendance=1000,
            home_team_score=2, away_team_score=1, added_time=3, completed=True
        )

        # Register players with their respective teams and the competition
        self.registration1 = PlayerRegistration.objects.create(player=self.player1, team=self.team1, competition=self.competition)
        self.registration2 = PlayerRegistration.objects.create(player=self.player2, team=self.team2, competition=self.competition)

    def test_match_creation(self):
        self.assertEqual(self.match.competition, self.competition)
        self.assertEqual(self.match.home_team, self.team1)
        self.assertEqual(self.match.away_team, self.team2)

    def test_result_creation(self):
        self.assertEqual(self.result.match, self.match)
        self.assertEqual(self.result.referee, self.referee)
        self.assertEqual(self.result.home_team_score, 2)
        self.assertEqual(self.result.away_team_score, 1)

    def test_match_statistic_creation(self):
        match_stat = MatchStatistic.objects.create(
            match=self.match, team=self.team1, possession_percentage=60.0,
            shots_on_goal=10, total_shots=15, fouls=5, corners=7, offsides=2
        )
        self.assertEqual(match_stat.match, self.match)
        self.assertEqual(match_stat.team, self.team1)
        self.assertEqual(match_stat.possession_percentage, 60.0)

    def test_save_creation(self):
        save = Save.objects.create(match=self.match, goalkeeper=self.player1, minute=45)
        self.assertEqual(save.match, self.match)
        self.assertEqual(save.goalkeeper, self.player1)
        self.assertEqual(save.minute, 45)

    def test_goal_creation(self):
        goal = Goal.objects.create(match=self.match, scoring_team=self.team1, scorer=self.player1, assist=self.player2, minute=30)
        self.assertEqual(goal.match, self.match)
        self.assertEqual(goal.scoring_team, self.team1)
        self.assertEqual(goal.scorer, self.player1)
        self.assertEqual(goal.assist, self.player2)
        self.assertEqual(goal.minute, 30)

    def test_penalty_creation(self):
        penalty = Penalty.objects.create(match=self.match, player=self.player1, minute=60, is_missed=False)
        self.assertEqual(penalty.match, self.match)
        self.assertEqual(penalty.player, self.player1)
        self.assertEqual(penalty.minute, 60)
        self.assertFalse(penalty.is_missed)

    def test_foul_creation(self):
        foul = Foul.objects.create(match=self.match, player_committed=self.player1, player_suffered=self.player2, minute=50, description="Description")
        self.assertEqual(foul.match, self.match)
        self.assertEqual(foul.player_committed, self.player1)
        self.assertEqual(foul.player_suffered, self.player2)
        self.assertEqual(foul.minute, 50)
        self.assertEqual(foul.description, "Description")

    def test_card_creation(self):
        card = Card.objects.create(match=self.match, player=self.player1, card_type=Card.YELLOW, minute=70)
        self.assertEqual(card.match, self.match)
        self.assertEqual(card.player, self.player1)
        self.assertEqual(card.card_type, Card.YELLOW)
        self.assertEqual(card.minute, 70)

    def test_substitution_creation(self):
        substitution = Substitution.objects.create(match=self.match, team=self.team1, player_out=self.player1, player_in=self.player2, minute=80)
        self.assertEqual(substitution.match, self.match)
        self.assertEqual(substitution.team, self.team1)
        self.assertEqual(substitution.player_out, self.player1)
        self.assertEqual(substitution.player_in, self.player2)
        self.assertEqual(substitution.minute, 80)

    def test_injury_creation(self):
        injury = Injury.objects.create(match=self.match, player=self.player1, minute=90, severity="Severe")
        self.assertEqual(injury.match, self.match)
        self.assertEqual(injury.player, self.player1)
        self.assertEqual(injury.minute, 90)
        self.assertEqual(injury.severity, "Severe")

    def test_result_standing_update(self):
        home_standing = Standing.objects.get(competition=self.competition, team=self.team1)
        away_standing = Standing.objects.get(competition=self.competition, team=self.team2)
        self.assertEqual(home_standing.points, 3)
        self.assertEqual(home_standing.goals_for, 2)
        self.assertEqual(home_standing.goals_against, 1)
        self.assertEqual(away_standing.points, 0)
        self.assertEqual(away_standing.goals_for, 1)
        self.assertEqual(away_standing.goals_against, 2)

    def test_result_delete_standing_update(self):
        self.result.delete()
        home_standing = Standing.objects.get(competition=self.competition, team=self.team1)
        away_standing = Standing.objects.get(competition=self.competition, team=self.team2)
        self.assertEqual(home_standing.points, 0)
        self.assertEqual(home_standing.goals_for, 0)
        self.assertEqual(home_standing.goals_against, 0)
        self.assertEqual(away_standing.points, 0)
        self.assertEqual(away_standing.goals_for, 0)
        self.assertEqual(away_standing.goals_against, 0)
