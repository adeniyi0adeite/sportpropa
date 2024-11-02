from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Coach, Team, TeamComment, TeamLike, Competition, CupGroup, CompetitionComment,
    CompetitionLike, Player, PlayerRegistration, PlayerPost, PlayerComment, PlayerLike, Referee, TeamCoachCompetition
)


class CoachAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'location', 'current_team_display', 'picture_thumbnail')
    search_fields = ('first_name', 'last_name', 'location')

    def current_team_display(self, obj):
        team = obj.current_team()
        return team.name if team else "No team"
    current_team_display.short_description = 'Current Team'

    def picture_thumbnail(self, obj):
        if obj.picture:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.picture.url)
        return "No Picture"
    picture_thumbnail.short_description = 'Picture'

admin.site.register(Coach, CoachAdmin)



class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'founded_year', 'coach')
    search_fields = ('name', 'location', 'coach__first_name', 'coach__last_name')

admin.site.register(Team, TeamAdmin)


class TeamCommentAdmin(admin.ModelAdmin):
    list_display = ('team', 'author', 'content', 'created_at')
    search_fields = ('team__name', 'author__user__username', 'content')

admin.site.register(TeamComment, TeamCommentAdmin)


class TeamLikeAdmin(admin.ModelAdmin):
    list_display = ('team', 'user', 'comment', 'created_at')
    search_fields = ('team__name', 'user__user__username', 'comment__content')

admin.site.register(TeamLike, TeamLikeAdmin)


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'organizer', 'location', 'competition_type', 'prize', 'registration_open', 'created_at')
    search_fields = ('name', 'organizer', 'location', 'competition_type')

admin.site.register(Competition, CompetitionAdmin)


class CupGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'competition')
    search_fields = ('name', 'competition__name')

admin.site.register(CupGroup, CupGroupAdmin)


class CompetitionCommentAdmin(admin.ModelAdmin):
    list_display = ('competition', 'author', 'content', 'created_at')
    search_fields = ('competition__name', 'author__user__username', 'content')

admin.site.register(CompetitionComment, CompetitionCommentAdmin)


class CompetitionLikeAdmin(admin.ModelAdmin):
    list_display = ('competition', 'user', 'comment', 'created_at')
    search_fields = ('competition__name', 'user__user__username', 'comment__content')

admin.site.register(CompetitionLike, CompetitionLikeAdmin)


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'nationality', 'team', 'position', 'age', 'total_games')
    search_fields = ('name__username', 'nationality', 'team__name', 'position')

admin.site.register(Player, PlayerAdmin)


class PlayerRegistrationAdmin(admin.ModelAdmin):
    list_display = ('player', 'team', 'competition')
    search_fields = ('player__name__username', 'team__name', 'competition__name')

admin.site.register(PlayerRegistration, PlayerRegistrationAdmin)


class PlayerPostAdmin(admin.ModelAdmin):
    list_display = ('player', 'uploaded_at')
    search_fields = ('player__name__username', 'caption')

admin.site.register(PlayerPost, PlayerPostAdmin)


class PlayerCommentAdmin(admin.ModelAdmin):
    list_display = ('player', 'author', 'content', 'created_at')
    search_fields = ('player__name__username', 'author__user__username', 'content')

admin.site.register(PlayerComment, PlayerCommentAdmin)


class PlayerLikeAdmin(admin.ModelAdmin):
    list_display = ('player', 'user', 'comment', 'created_at')
    search_fields = ('player__name__username', 'user__user__username', 'comment__content')

admin.site.register(PlayerLike, PlayerLikeAdmin)


class RefereeAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'birth_date')
    search_fields = ('name', 'country')

admin.site.register(Referee, RefereeAdmin)


# New Admin for TeamCoachCompetition
class TeamCoachCompetitionAdmin(admin.ModelAdmin):
    list_display = ('team', 'coach', 'competition', 'role', 'date_assigned')
    search_fields = ('team__name', 'coach__first_name', 'coach__last_name', 'competition__name', 'role')

admin.site.register(TeamCoachCompetition, TeamCoachCompetitionAdmin)
