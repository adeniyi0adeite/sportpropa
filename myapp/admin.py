from django.contrib import admin

# Register your models here.
from .models import Feedback, SoccerNews, Contact, Award






# Dynamic registration of models without customization
models = [ Feedback, Contact ]

for model in models:
    admin.site.register(model)



@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ('get_award_name', 'competition', 'category', 'date_awarded', 'get_award_winner')
    search_fields = ('description',)

    def get_award_name(self, obj):
        return obj.get_award_name()
    get_award_name.short_description = 'Award Name'

    def get_award_winner(self, obj):
        if obj.category == Award.PLAYER and obj.player:
            return obj.player.name.get_full_name()
        elif obj.category == Award.COACH and obj.coach:
            return obj.coach.name
        elif obj.category == Award.REFEREE and obj.referee:
            return obj.referee.name
        elif obj.category == Award.TEAM and obj.team:
            return obj.team.name
        return 'N/A'
    get_award_winner.short_description = 'Award Winner'



@admin.register(SoccerNews)
class SoccerNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date')
    list_filter = ('published_date',)
    search_fields = ('title', 'summary')

