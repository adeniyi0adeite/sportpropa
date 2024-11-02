from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.files.storage import default_storage
import os 
# Create your models here.

from competition_management.models import Competition, Player, Referee, Coach, Team


class Feedback(models.Model):
    FEEDBACK_TYPE_CHOICES = [
        ('website', 'Website Navigation'),
        ('content', 'Content Quality'),
        ('feature', 'Feature Request'),
        ('bug', 'Bug Report'),
    ]
    
    name = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    feedback_type = models.CharField(max_length=100, choices=FEEDBACK_TYPE_CHOICES, default='website')
    experience_rating = models.IntegerField(default=0)  # Assuming rating is an integer
    suggestions = models.TextField(blank=True, null=True)
    message = models.TextField()
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name} submitted on {self.submitted_on}"



class SoccerNews(models.Model):
    NEWS_TYPES = (
        ('HOT', 'Hot'),
        ('TRENDING', 'Trending'),
    )

    title = models.CharField(max_length=255)
    summary = models.TextField()
    news_url = models.URLField()
    image = models.ImageField(upload_to='news_images/')
    published_date = models.DateTimeField()
    news_type = models.CharField(max_length=10, choices=NEWS_TYPES, default='HOT')

    def __str__(self):
        return self.title
    

class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    message = models.TextField()
    email = models.EmailField()

    def __str__(self):
        return self.name
    


class Award(models.Model):
    PLAYER = 'Player'
    COACH = 'Coach'
    REFEREE = 'Referee'
    TEAM = 'Team'
    AWARD_CATEGORIES = [
        (PLAYER, 'Player'),
        (COACH, 'Coach'),
        (REFEREE, 'Referee'),
        (TEAM, 'Team'),
    ]

    MAN_OF_THE_MATCH = 'Man of the Match'
    BEST_GOALKEEPER = 'Best Goalkeeper'
    BEST_PLAYER = 'Best Player'
    TOP_SCORER = 'Top Scorer'
    TOP_ASSIST = 'Top Assist'

    PLAYER_AWARDS = [
        (MAN_OF_THE_MATCH, 'Man of the Match'),
        (BEST_GOALKEEPER, 'Best Goalkeeper'),
        (BEST_PLAYER, 'Best Player'),
        (TOP_SCORER, 'Top Scorer'),
        (TOP_ASSIST, 'Top Assist'),
    ]

    BEST_COACH = 'Best Coach'
    COACH_AWARDS = [
        (BEST_COACH, 'Best Coach'),
    ]

    BEST_REFEREE = 'Best Referee'
    REFEREE_AWARDS = [
        (BEST_REFEREE, 'Best Referee'),
    ]

    BEST_TEAM = 'Best Team'
    FAIR_PLAY = 'Fair Play'
    TEAM_AWARDS = [
        (BEST_TEAM, 'Best Team'),
        (FAIR_PLAY, 'Fair Play'),
    ]

    description = models.TextField(blank=True, null=True)
    date_awarded = models.DateField()
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='awards')
    category = models.CharField(max_length=10, choices=AWARD_CATEGORIES)
    player_award = models.CharField(max_length=20, choices=PLAYER_AWARDS, blank=True, null=True)
    coach_award = models.CharField(max_length=20, choices=COACH_AWARDS, blank=True, null=True)
    referee_award = models.CharField(max_length=20, choices=REFEREE_AWARDS, blank=True, null=True)
    team_award = models.CharField(max_length=20, choices=TEAM_AWARDS, blank=True, null=True)
    player = models.ForeignKey(Player, related_name='awards', on_delete=models.SET_NULL, blank=True, null=True)
    referee = models.ForeignKey(Referee, related_name='awards', on_delete=models.SET_NULL, blank=True, null=True)
    coach = models.ForeignKey(Coach, related_name='awards', on_delete=models.SET_NULL, blank=True, null=True)
    team = models.ForeignKey(Team, related_name='awards', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        award_name = self.get_award_name()
        return f"{award_name} ({self.category})"

    def get_award_name(self):
        if self.category == self.PLAYER:
            return self.player_award or 'Player Award'
        elif self.category == self.COACH:
            return self.coach_award or 'Coach Award'
        elif self.category == self.REFEREE:
            return self.referee_award or 'Referee Award'
        elif self.category == self.TEAM:
            return self.team_award or 'Team Award'
        return 'Award'