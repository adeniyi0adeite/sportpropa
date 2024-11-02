from standing_management.models import Standing
from .models import Team

def calculate_standings(competition, registered_teams):
    """
    Calculate standings for a given competition and registered teams.
    Returns a dictionary with group standings if the competition has a group stage.
    """
    if competition.is_group_stage:
        groups = competition.groups.all()
        standings = {}
        for group in groups:
            group_teams = group.teams.filter(id__in=registered_teams.values_list('id', flat=True))
            group_standings = Standing.objects.filter(competition=competition, group=group, team__in=group_teams)
            standings[group] = group_standings.prefetch_related('team').order_by('-points', '-goals_for')

            missing_teams = group_teams.exclude(id__in=group_standings.values_list('team__id', flat=True))
            for team in missing_teams:
                Standing.objects.create(competition=competition, group=group, team=team)
        return standings
    else:
        standings = Standing.objects.filter(competition=competition, team__in=registered_teams).prefetch_related('team').order_by('-points', '-goals_for')
        missing_teams = registered_teams.exclude(id__in=standings.values_list('team__id', flat=True))
        for team in missing_teams:
            Standing.objects.create(competition=competition, team=team)
        return standings
