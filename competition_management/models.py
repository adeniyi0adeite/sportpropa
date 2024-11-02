from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from PIL import Image
import os
from django.core.validators import FileExtensionValidator

from user_management.models import UserProfile
from standing_management.models import Standing

# Create your models here.




class Coach(models.Model):
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    picture = models.ImageField(upload_to='coach_pictures/', blank=True, null=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def current_team(self):
        # Find the most recent team assignment for the coach
        latest_registration = TeamCoachCompetition.objects.filter(coach=self).order_by('-date_assigned').first()
        if latest_registration:
            return latest_registration.team
        return None

    def __str__(self):
        return self.full_name()

    def delete(self, *args, **kwargs):
        # If there is a picture associated with the coach, delete it from the filesystem
        if self.picture and default_storage.exists(self.picture.name):
            default_storage.delete(self.picture.name)
        super().delete(*args, **kwargs)

    

class Team(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='team_logos/', default='default/soccer.png', blank=True, null=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    coach = models.ForeignKey(Coach, related_name='teams_coached', on_delete=models.CASCADE, null=True, blank=True)


    # Add more fields as needed
    
    def __str__(self):
        return self.name
    

class TeamComment(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='team_replies', null=True, blank=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"Comment by {self.author}"
    
class TeamLike(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='team_likes')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    comment = models.ForeignKey(TeamComment, on_delete=models.CASCADE, null=True, blank=True, related_name='team_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user}"


class Competition(models.Model):
    LEAGUE = 'League'
    CUP = 'Cup'
    COMPETITION_TYPES = [
        (LEAGUE, 'League'),
        (CUP, 'Cup'),
    ]

    name = models.CharField(max_length=100)
    organizer = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(default='No description provided')
    prize = models.CharField(max_length=50)
    registration_open = models.BooleanField(default=True)
    logo = models.ImageField(upload_to='competition_logos/', null=True, blank=True)
    teams = models.ManyToManyField(Team, related_name='competitions', blank=True)
    competition_type = models.CharField(max_length=10, choices=COMPETITION_TYPES, default=LEAGUE)
    is_group_stage = models.BooleanField(default=False)
    is_school_competition = models.BooleanField(default=False)  # New field to distinguish school competitions
    created_at = models.DateTimeField(null=True, blank=True)  # Allow null and blank

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        if not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.competition_type}) - created on {self.created_at}"


class CupGroup(models.Model):
    competition = models.ForeignKey(Competition, related_name='groups', on_delete=models.CASCADE, limit_choices_to={'competition_type': Competition.CUP})
    name = models.CharField(max_length=100)
    teams = models.ManyToManyField(Team, related_name='groups')  # Establishing many-to-many relationship with Team

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the original save method to ensure the group is saved first
        # Create standings for each team associated with the group
        for team in self.teams.all():
            Standing.objects.get_or_create(competition=self.competition, group=self, team=team, defaults={'points': 0, 'goals_for': 0, 'goals_against': 0})




class CompetitionComment(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='competition_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='competition_replies', null=True, blank=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"Comment by {self.author}"
    
class CompetitionLike(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True, blank=True, related_name='competition_likes')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    comment = models.ForeignKey(CompetitionComment, on_delete=models.CASCADE, null=True, blank=True, related_name='competition_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user}"




class TeamCoachCompetition(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, null=True, blank=True)  # e.g., Head Coach, Assistant Coach
    date_assigned = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.team.name} coached by {self.coach.full_name()} in {self.competition.name}"




class Player(models.Model):

    GOALKEEPER = 'GK'
    DEFENDER = 'DF'
    CENTRE_BACK = 'CB'
    FULL_BACK = 'FB'
    WING_BACK = 'WB'
    MIDFIELDER = 'CM'
    DEFENSIVE_MIDFIELDER = 'DM'
    CENTER_MIDFIELDER = 'CM'
    ATTACKING_MIDFIELDER = 'AM'
    WINGER = 'WG'
    FORWARD = 'FW'
    CENTER_FORWARD = 'CF'
    STRIKER = 'ST'
    UTILITY_PLAYER = 'UT'

    PLAYER_POSITIONS = [
        (GOALKEEPER, 'Goalkeeper'), 
        (DEFENDER, 'Defender'),
        (CENTRE_BACK, 'Center Back'), 
        (FULL_BACK, 'Full Back'), 
        (WING_BACK, 'Wing Back'), 
        (MIDFIELDER, 'Midfielder'), 
        (DEFENSIVE_MIDFIELDER, 'Defensive Midfielder'), 
        (CENTER_MIDFIELDER, 'Center Midfielder'), 
        (ATTACKING_MIDFIELDER, 'Attacking Midfielder'), 
        (WINGER, 'Winger'),
        (FORWARD, 'Forward'), 
        (CENTER_FORWARD, 'Centre Forward'), 
        (STRIKER, 'Striker'),
        (UTILITY_PLAYER, 'Utility Player'), # This is for players who can play in multiple positions
    ]


        
    name = models.OneToOneField(User, on_delete=models.CASCADE)
    nationality = models.CharField(max_length=255, blank=True, default='N/A')
    picture = models.ImageField(upload_to='player_image/', blank=True, null=True)
    team = models.ForeignKey(Team, related_name='players', on_delete=models.CASCADE, null=True)
    position = models.CharField(max_length=2, choices=PLAYER_POSITIONS, default='N/A')
    age = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)  # Assuming weight in kg
    total_games = models.IntegerField(default=0)  # Defaulting to 0 games if not specified
    height = models.IntegerField(null=True, blank=True)  # Assuming height in meters
    foot = models.CharField(max_length=10, choices=[('Left', 'Left'), ('Right', 'Right'), ('Both', 'Both')], default='Right')
    biography = models.TextField(blank=True, null=True)



    # Add more fields as needed


    class Meta:
        unique_together = ('name', 'team')
        
    def delete(self, *args, **kwargs):
        # If there is a picture associated with the player, delete it from the filesystem
        if self.picture:
            if default_storage.exists(self.picture.name):
                default_storage.delete(self.picture.name)
        
        # Delete the associated user
        self.name.delete()
        
        # Call the superclass method to handle default deletion
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name.get_full_name()
    


class PlayerRegistration(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='registrations')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='player_registrations')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='player_registrations')

    class Meta:
        unique_together = ('player', 'competition', 'team')  # Ensure uniqueness across these fields

    def __str__(self):
        return f"{self.player} registered to {self.team} in ({self.competition})"



class PlayerPost(models.Model):
    player = models.ForeignKey('Player', related_name='posts', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='player_images/', null=True, blank=True)
    video = models.FileField(upload_to='player_videos/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov'])])
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.name.get_full_name()} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

    def delete(self, *args, **kwargs):
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        if self.video and os.path.isfile(self.video.path):
            os.remove(self.video.path)
        super().delete(*args, **kwargs)







class PlayerComment(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='player_replies', null=True, blank=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"Comment by {self.author}"
    
class PlayerLike(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True, related_name='player_likes')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    comment = models.ForeignKey(PlayerComment, on_delete=models.CASCADE, null=True, blank=True, related_name='player_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user}"




class Vote(models.Model):
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='votes')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'player', 'competition')  # Ensure unique vote per user, player, and competition

    def __str__(self):
        return f"Vote by {self.user} for {self.player} in {self.competition}"



class Referee(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    birth_date = models.DateField()


    def __str__(self):
        return self.name




