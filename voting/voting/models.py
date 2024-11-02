from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.crypto import get_random_string

from competition_management.models import Competition, Player, Team, Coach


class AwardCategory(models.Model):
    CATEGORY_CHOICES = [
        ('most_valuable_player', 'MVP'),
        ('man_of_the_match', 'Man of the Match'),
        ('best_player', 'Best Player'),
        ('top_scorer', 'Top Scorer'),
        ('best_goalkeeper', 'Best Goalkeeper'),
        ('best_team', 'Best Team'),
        ('best_coach', 'Best Coach'),
    ]

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    nominees = models.ManyToManyField(Player, blank=True)
    teams = models.ManyToManyField(Team, blank=True)
    coaches = models.ManyToManyField(Coach, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    close_date = models.DateTimeField(null=True, blank=True)
    hide_vote_count = models.BooleanField(default=False)  # Updated field

    def __str__(self):
        return f"{self.category} for {self.competition}"

    def is_voting_active(self):
        now = timezone.now()
        return self.start_date <= now <= (self.close_date or now)

    def get_winner(self):
        # Count votes based on category
        if self.category == 'man_of_the_match':
            return self.nominees.first()

        elif self.category == 'best_team':
            votes = Vote.objects.filter(competition=self.competition, team__isnull=False, category=self.category).values('team').annotate(total_votes=Sum('num_of_votes')).order_by('-total_votes')
            if votes:
                team_id = votes[0]['team']
                return Team.objects.get(id=team_id)

        elif self.category == 'best_coach':
            votes = Vote.objects.filter(competition=self.competition, coach__isnull=False, category=self.category).values('coach').annotate(total_votes=Sum('num_of_votes')).order_by('-total_votes')
            if votes:
                coach_id = votes[0]['coach']
                return Coach.objects.get(id=coach_id)

        else:
            votes = Vote.objects.filter(competition=self.competition, player__isnull=False, category=self.category).values('player').annotate(total_votes=Sum('num_of_votes')).order_by('-total_votes')
            if votes:
                player_id = votes[0]['player']
                return Player.objects.get(id=player_id)

        return None

    def winner_display(self):
        now = timezone.now()
        if self.close_date and now < self.close_date:
            return "No winner determined yet; voting is still open."
        
        winner = self.get_winner()
        if not winner:
            return "No winner determined yet"
        return winner

    def display_votes(self, item):
        """Hides vote count if hide_vote_count is True."""
        if self.hide_vote_count:
            return "Votes hidden"
        else:
            # Example for player/team votes
            if isinstance(item, Player):
                return Vote.objects.filter(competition=self.competition, player=item, category=self.category).aggregate(total_votes=Sum('num_of_votes'))['total_votes'] or 0
            elif isinstance(item, Team):
                return Vote.objects.filter(competition=self.competition, team=item, category=self.category).aggregate(total_votes=Sum('num_of_votes'))['total_votes'] or 0
            elif isinstance(item, Coach):
                return Vote.objects.filter(competition=self.competition, coach=item, category=self.category).aggregate(total_votes=Sum('num_of_votes'))['total_votes'] or 0


class Vote(models.Model):
    email = models.EmailField()
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_votes', blank=True, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True, related_name='team_votes')
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, blank=True, null=True, related_name='coach_votes')  # New field for coach votes
    num_of_votes = models.PositiveIntegerField(default=1)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_status = models.BooleanField(default=False)
    transaction_reference = models.CharField(max_length=100, null=True, blank=True)
    confirmation_id = models.CharField(max_length=100, blank=True, null=True)
    confirmed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, blank=True, null=True)  # Category for the vote

    def save(self, *args, **kwargs):
        if not self.confirmation_id:
            confirmation_code = get_random_string(8, '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
            self.confirmation_id = f"{confirmation_code}-{self.id}"
        self.amount_paid = self.num_of_votes * 100  # 100 Naira per vote
        super().save(*args, **kwargs)

    def __str__(self):
        if self.team:
            return f"Vote by {self.email} for {self.num_of_votes} votes for team {self.team} in {self.competition}"
        elif self.coach:
            return f"Vote by {self.email} for {self.num_of_votes} votes for coach {self.coach} in {self.competition}"
        return f"Vote by {self.email} for {self.num_of_votes} votes for player {self.player} in {self.competition}"
