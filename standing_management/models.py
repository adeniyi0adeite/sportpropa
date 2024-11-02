from django.db import models, IntegrityError
from django.core.files.storage import default_storage


# Create your models here.


class Standing(models.Model):
    competition = models.ForeignKey('competition_management.Competition', on_delete=models.CASCADE, related_name='standings')
    group = models.ForeignKey('competition_management.CupGroup', related_name='standings', on_delete=models.CASCADE, null=True, blank=True)
    team = models.ForeignKey('competition_management.Team', on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)
    goals_for = models.PositiveIntegerField(default=0)
    goals_against = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against

    def __str__(self):
        # Include the group name if it exists
        if self.group:
            return f"{self.team.name} in {self.competition.name} - {self.group.name}"
        else:
            return f"{self.team.name} in {self.competition.name}"
