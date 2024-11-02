from django.contrib import admin
from .models import Vote, AwardCategory

class VoteAdmin(admin.ModelAdmin):
    list_display = ('email', 'competition', 'category', 'player', 'team', 'num_of_votes', 'amount_paid', 'payment_status', 'confirmed', 'confirmation_id', 'timestamp')
    list_filter = ('competition', 'category', 'player', 'team', 'payment_status', 'confirmed')
    search_fields = ('email', 'player__name', 'team__name', 'category', 'transaction_reference')
    ordering = ('-timestamp',)
    readonly_fields = ('category', 'transaction_reference', 'confirmation_id', 'timestamp')

class AwardCategoryAdmin(admin.ModelAdmin):
    list_display = ('competition', 'category', 'start_date', 'close_date', 'winner_display', 'is_vote_count_hidden')
    list_filter = ('competition', 'category', 'hide_vote_count')  # Added filter for hide_vote_count
    search_fields = ('competition__name', 'category')
    ordering = ('-start_date',)

    def is_vote_count_hidden(self, obj):
        """Display if the vote count is hidden."""
        return "Yes" if obj.hide_vote_count else "No"
    is_vote_count_hidden.short_description = "Vote Count Hidden"  # Set the column title

admin.site.register(Vote, VoteAdmin)
admin.site.register(AwardCategory, AwardCategoryAdmin)
