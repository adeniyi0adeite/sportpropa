from django.contrib import admin
from .models import Match, Goal, Save, Foul, Card, Substitution, MatchStatistic, Result, Injury, PenaltyShootout




class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_info', 'competition_display', 'match_date', 'location')  # Removed 'man_of_the_match'
    search_fields = ('home_team__name', 'away_team__name', 'competition__name', 'match_type', 'group__name')

    def match_info(self, obj):
        match_info = f"{obj.home_team} vs {obj.away_team}"
        if obj.group:
            match_info += f" ({obj.group.name})"
        if obj.match_type:
            match_info += f" ({obj.get_match_type_display()})"
        return match_info
    match_info.short_description = 'Match Info'

    def competition_display(self, obj):
        return f"{obj.competition.name} - {obj.competition.get_competition_type_display()}"
    competition_display.short_description = 'Competition'

admin.site.register(Match, MatchAdmin)



class ResultAdmin(admin.ModelAdmin):
    list_display = ('match_display', 'competition_display', 'home_team_score', 'away_team_score', 'completed', 'referee', 'attendance', 'man_of_the_match')  # Added 'man_of_the_match'
    search_fields = ('match__home_team__name', 'match__away_team__name', 'match__competition__name')

    def match_display(self, obj):
        match_info = f"{obj.match.home_team} vs {obj.match.away_team}"
        if obj.match.group:
            match_info += f" ({obj.match.group.name})"
        if obj.match.match_type:
            match_info += f" ({obj.match.get_match_type_display()})"
        return match_info
    match_display.short_description = 'Match Info'

    def competition_display(self, obj):
        return f"{obj.match.competition.name} - {obj.match.competition.get_competition_type_display()}"
    competition_display.short_description = 'Competition'

admin.site.register(Result, ResultAdmin)



class MatchStatisticAdmin(admin.ModelAdmin):
    list_display = ('match', 'team', 'possession_percentage', 'shots_on_goal', 'total_shots', 'fouls', 'corners', 'offsides')

admin.site.register(MatchStatistic, MatchStatisticAdmin)


class SaveAdmin(admin.ModelAdmin):
    list_display = ('match', 'goalkeeper', 'minute')

admin.site.register(Save, SaveAdmin)


class GoalAdmin(admin.ModelAdmin):
    list_display = ('match', 'scoring_team', 'scorer', 'assist', 'is_own_goal', 'minute')

admin.site.register(Goal, GoalAdmin)



class FoulAdmin(admin.ModelAdmin):
    list_display = ('match', 'player_committed', 'player_suffered', 'minute', 'description')

admin.site.register(Foul, FoulAdmin)


class CardAdmin(admin.ModelAdmin):
    list_display = ('match', 'player', 'card_type', 'minute')

admin.site.register(Card, CardAdmin)


class SubstitutionAdmin(admin.ModelAdmin):
    list_display = ('match', 'team', 'player_out', 'player_in', 'minute')

admin.site.register(Substitution, SubstitutionAdmin)


class InjuryAdmin(admin.ModelAdmin):
    list_display = ('match', 'player', 'minute', 'severity')

admin.site.register(Injury, InjuryAdmin)


class PenaltyShootoutAdmin(admin.ModelAdmin):
    list_display = ('result', 'team', 'player', 'minute', 'is_shootout', 'is_missed', 'is_scored',)
    
admin.site.register(PenaltyShootout, PenaltyShootoutAdmin)