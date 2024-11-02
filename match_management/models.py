from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.files.storage import default_storage

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from competition_management.models import Competition, CupGroup, Team, Player, PlayerRegistration, Referee
from standing_management.models import Standing
from user_management.models import UserProfile


# Create your models here.



class Match(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='matches')
    group = models.ForeignKey(CupGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches')
    MATCH_TYPE_CHOICES = [
        ('Round of 16', 'Round of 16'),
        ('Quarter Final', 'Quarter final'),
        ('Semi Final', 'Semi final'),
        ('Third Place', 'Third Place'),
        ('Final', 'Final'),
    ]
    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES, null=True, blank=True)
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    match_date = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=255, blank=True)
    

    def __str__(self):
        match_info = f"{self.home_team} vs {self.away_team} - {self.competition}"
        if self.group:
            match_info += f" ({self.group.name})"
        if self.match_type:
            match_info += f" ({self.get_match_type_display()})"
        match_info += f" on {self.match_date.strftime('%Y-%m-%d')}"
        return match_info
    


class MatchComment(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='match_replies', null=True, blank=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"Comment by {self.author} on match {self.match}"

class MatchLike(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, blank=True, related_name='match_likes')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    comment = models.ForeignKey(MatchComment, on_delete=models.CASCADE, null=True, blank=True, related_name='match_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user} on match or comment {self.match or self.comment}"





    
class Result(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, primary_key=True, related_name='details')
    referee = models.ForeignKey(Referee, on_delete=models.SET_NULL, null=True, blank=True)
    attendance = models.IntegerField(null=True, blank=True)
    home_team_score = models.PositiveIntegerField(default=0)
    away_team_score = models.PositiveIntegerField(default=0)
    added_time = models.IntegerField(default=0, help_text="Amount of added time in minutes")
    completed = models.BooleanField(default=False)  # Indicates if the match has been played and completed
    man_of_the_match = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)

    # Store previous scores for comparison
    _old_home_team_score = None
    _old_away_team_score = None

    def save(self, *args, **kwargs):
        if self.pk:  # Check if the object already exists
            try:
                old_result = Result.objects.get(pk=self.pk)
                self._old_home_team_score = old_result.home_team_score
                self._old_away_team_score = old_result.away_team_score
            except Result.DoesNotExist:
                # Handle case where the old result might not exist (it shouldn't normally happen)
                self._old_home_team_score = 0
                self._old_away_team_score = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.match} details"



# signals
@receiver(post_save, sender=Result)
def update_standings(sender, instance, created, **kwargs):
    # Check if the competition type is CUP and if it has a CupGroup
    if created:  # If the result is newly created
        if instance.match.competition.competition_type == Competition.CUP and instance.match.group:
            update_standing(instance)
    else:  # If the result is being updated
        if instance.match.competition.competition_type == Competition.CUP and instance.match.group:
            if instance._old_home_team_score is not None and instance._old_away_team_score is not None:
                update_standing(instance, is_update=True)

def update_standing(result, is_update=False):
    # Check if the competition is a CUP and if it has a group
    if result.match.competition.competition_type == Competition.CUP and result.match.group:
        # Update home team standing
        home_standing = Standing.objects.get(competition=result.match.competition, team=result.match.home_team)

        if is_update:
            # Adjust for old scores
            if result._old_home_team_score > result._old_away_team_score:  # Previous win
                home_standing.wins -= 1
                home_standing.points -= 3
            elif result._old_home_team_score < result._old_away_team_score:  # Previous loss
                home_standing.losses -= 1
            else:  # Previous draw
                home_standing.draws -= 1
                home_standing.points -= 1

            # Remove old goals
            home_standing.goals_for -= result._old_home_team_score
            home_standing.goals_against -= result._old_away_team_score

        # Update with new scores
        home_standing.goals_for += result.home_team_score
        home_standing.goals_against += result.away_team_score

        # Calculate new outcomes
        if result.home_team_score > result.away_team_score:  # New win
            home_standing.wins += 1
            home_standing.points += 3
        elif result.home_team_score < result.away_team_score:  # New loss
            home_standing.losses += 1
        else:  # New draw
            home_standing.draws += 1
            home_standing.points += 1

        home_standing.save()

        # Update away team standing
        away_standing = Standing.objects.get(competition=result.match.competition, team=result.match.away_team)

        if is_update:
            # Adjust for old scores
            if result._old_away_team_score > result._old_home_team_score:  # Previous win
                away_standing.wins -= 1
                away_standing.points -= 3
            elif result._old_away_team_score < result._old_home_team_score:  # Previous loss
                away_standing.losses -= 1
            else:  # Previous draw
                away_standing.draws -= 1
                away_standing.points -= 1

            # Remove old goals
            away_standing.goals_for -= result._old_away_team_score
            away_standing.goals_against -= result._old_home_team_score

        # Update with new scores
        away_standing.goals_for += result.away_team_score
        away_standing.goals_against += result.home_team_score

        # Calculate new outcomes
        if result.away_team_score > result.home_team_score:  # New win
            away_standing.wins += 1
            away_standing.points += 3
        elif result.away_team_score < result.home_team_score:  # New loss
            away_standing.losses += 1
        else:  # New draw
            away_standing.draws += 1
            away_standing.points += 1

        away_standing.save()

@receiver(post_delete, sender=Result)
def update_standing_on_delete(sender, instance, **kwargs):
    # Identify the home and away teams from the deleted result
    home_team = instance.match.home_team
    away_team = instance.match.away_team
    competition = instance.match.competition

    # Get the corresponding standings for home and away teams
    try:
        home_standing = Standing.objects.get(competition=competition, team=home_team)
        away_standing = Standing.objects.get(competition=competition, team=away_team)

        # Adjust standings based on the deleted result
        if instance.home_team_score > instance.away_team_score:  # Previous home win
            home_standing.wins -= 1
            home_standing.points -= 3
            away_standing.losses -= 1
        elif instance.home_team_score < instance.away_team_score:  # Previous away win
            away_standing.wins -= 1
            away_standing.points -= 3
            home_standing.losses -= 1
        else:  # Previous draw
            home_standing.draws -= 1
            away_standing.draws -= 1
            home_standing.points -= 1
            away_standing.points -= 1

        # Remove goals from standings
        home_standing.goals_for -= instance.home_team_score
        home_standing.goals_against -= instance.away_team_score
        away_standing.goals_for -= instance.away_team_score
        away_standing.goals_against -= instance.home_team_score

        # Save the updated standings
        home_standing.save()
        away_standing.save()

    except Standing.DoesNotExist:
        # Handle case where standings may not exist (if necessary)
        pass




class MatchStatistic(models.Model):
    match = models.ForeignKey(Match, related_name='statistics', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    possession_percentage = models.IntegerField(default=0)
    shots_on_goal = models.IntegerField(default=0)
    total_shots = models.IntegerField(default=0)
    fouls = models.IntegerField(default=0)
    corners = models.IntegerField(default=0)
    offsides = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.team} statistics for {self.match}"
    

class Save(models.Model):
    match = models.ForeignKey(Match, related_name='saves', on_delete=models.CASCADE)
    goalkeeper = models.ForeignKey(
        Player, 
        related_name='saves_made', 
        on_delete=models.CASCADE, 
        limit_choices_to={'position': Player.GOALKEEPER}
    )
    minute = models.IntegerField(help_text="Minute the save was made")

    def __str__(self):
        return f"{self.goalkeeper} save on {self.minute} - ({self.match})"
    
    
class Goal(models.Model):
    match = models.ForeignKey(Match, related_name='goals', on_delete=models.CASCADE)
    scoring_team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    scorer = models.ForeignKey(Player, related_name='goal_scored', on_delete=models.CASCADE)
    assist = models.ForeignKey(Player, related_name='goal_assisted', on_delete=models.CASCADE, null=True, blank=True)
    is_own_goal = models.BooleanField(default=False)
    minute = models.IntegerField()

    def __str__(self):
        if self.is_own_goal:
            return f"{self.scorer} scored an own goal at {self.minute} minute - ({self.match})"
        else:
            assist_info = f" - assisted by {self.assist}" if self.assist else ""
            return f"{self.scorer} scored for {self.scoring_team} at {self.minute} minute{assist_info} - ({self.match})"
        


class PenaltyShootout(models.Model):
    is_shootout = models.BooleanField(default=False)
    result = models.ForeignKey(Result, related_name='penalties', on_delete=models.CASCADE, null=True, blank=True)
    team = models.ForeignKey(Team, related_name='penalty_plays', on_delete=models.CASCADE, null=True, blank=True)
    player = models.ForeignKey(Player, related_name='penalty_attempts', on_delete=models.CASCADE, null=True, blank=True)
    minute = models.IntegerField(null=True, blank=True)
    is_missed = models.BooleanField(default=False)
    is_scored = models.BooleanField(default=False)

    def __str__(self):
        outcome = "scored" if self.is_scored else "missed"
        player_name = self.player.name.get_full_name()  # Accessing the User model's get_full_name method
        return f"{self.minute}' Penalty {outcome} by {player_name} - {self.result.match}"  # Access match via result


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_scored and not self.is_shootout:
            Goal.objects.create(
                match=self.result.match,
                scoring_team=self.team,
                scorer=self.player,
                minute=self.minute,
                is_penalty=True
            )






class Foul(models.Model):
    match = models.ForeignKey(Match, related_name='fouls', on_delete=models.CASCADE)
    player_committed = models.ForeignKey(Player, related_name='fouls_committed', on_delete=models.CASCADE, help_text="The player who committed the foul")
    player_suffered = models.ForeignKey(Player, related_name='fouls_suffered', on_delete=models.CASCADE, null=True, blank=True, help_text="The player who suffered the foul (optional)")
    minute = models.IntegerField(help_text="Minute the foul occurred")
    description = models.TextField(blank=True, null=True, help_text="Description of the foul, e.g., type of foul, consequences")

    def __str__(self):
        return f"Foul by {self.player_committed.name} on {self.minute}'"



class Card(models.Model):
    YELLOW = 'Y'
    RED = 'R'
    CARD_CHOICES = [
        (YELLOW, 'Yellow'),
        (RED, 'Red'),
    ]

    match = models.ForeignKey(Match, related_name='cards', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    card_type = models.CharField(max_length=1, choices=CARD_CHOICES)
    minute = models.IntegerField()
    is_second_yellow = models.BooleanField(default=False)  # New field

    def clean(self):
        # Fetch the team(s) the player is registered to at the time of the match
        player_teams = PlayerRegistration.objects.filter(
            player=self.player,
            competition__matches=self.match  # Assuming there's a link from competition to matches
        ).values_list('team', flat=True)

        if not player_teams:
            raise ValidationError("No team found for player in this match.")

    def save(self, *args, **kwargs):
        if self.card_type == self.YELLOW:
            yellow_cards_count = Card.objects.filter(
                match=self.match, player=self.player, card_type=self.YELLOW
            ).count()

            if yellow_cards_count >= 1 and not self.is_second_yellow:
                # Update the current card to a red card instead of creating a new one
                self.card_type = self.RED
                self.is_second_yellow = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player} received a {self.get_card_type_display()} card on {self.minute}'"

    

class Substitution(models.Model):
    match = models.ForeignKey(Match, related_name='substitutions', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player_out = models.ForeignKey(Player, related_name='substituted_out', on_delete=models.CASCADE)
    player_in = models.ForeignKey(Player, related_name='substituted_in', on_delete=models.CASCADE)
    minute = models.IntegerField()

    def __str__(self):
        return f"{self.player_out} OFF, {self.player_in} IN in {self.minute}' minutes "


class Injury(models.Model):
    match = models.ForeignKey(Match, related_name='injuries', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    minute = models.IntegerField()
    severity = models.CharField(max_length=255, help_text='Brief description of the injury')

    def __str__(self):
        return f"{self.player} injured on {self.minute}' - {self.severity}"
    
