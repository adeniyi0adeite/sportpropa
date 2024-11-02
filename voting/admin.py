from django.contrib import admin
from django import forms
from .models import Vote, AwardCategory, Player, Team, Coach

class VoteAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'competition', 'category', 'player', 'team', 
        'num_of_votes', 'amount_paid', 'payment_status', 
        'confirmed', 'confirmation_id', 'timestamp'
    )
    list_filter = (
        'competition', 'category', 'player', 'team', 
        'payment_status', 'confirmed'
    )
    search_fields = ('email', 'player__name', 'team__name', 'category', 'transaction_reference')
    ordering = ('-timestamp',)
    readonly_fields = ('category', 'transaction_reference', 'confirmation_id', 'timestamp')

class AwardCategoryForm(forms.ModelForm):
    class Meta:
        model = AwardCategory
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize the queryset for nominees based on selected category
        if 'category' in self.data:
            category = self.data.get('category')
            if category == 'best_team':
                self.fields['teams'].queryset = Team.objects.all()
                self.fields['players'].queryset = Player.objects.none()
                self.fields['coaches'].queryset = Coach.objects.none()
            elif category == 'best_coach':
                self.fields['coaches'].queryset = Coach.objects.all()
                self.fields['teams'].queryset = Team.objects.none()
                self.fields['players'].queryset = Player.objects.none()
            else:  # Player-related categories
                self.fields['players'].queryset = Player.objects.all()
                self.fields['teams'].queryset = Team.objects.none()
                self.fields['coaches'].queryset = Coach.objects.none()
        else:
            # Default state when no category is selected
            self.fields['players'].queryset = Player.objects.all()
            self.fields['teams'].queryset = Team.objects.all()
            self.fields['coaches'].queryset = Coach.objects.all()

class AwardCategoryAdmin(admin.ModelAdmin):
    form = AwardCategoryForm
    list_display = ('competition', 'category', 'is_vote_count_hidden', 'start_date', 'is_closed', 'winner_display')
    list_filter = ('competition', 'category', 'hide_vote_count')
    search_fields = ('competition', 'category')
    ordering = ('-start_date',)

    def is_vote_count_hidden(self, obj):
        """Display if the vote count is hidden."""
        return "Yes" if obj.hide_vote_count else "No"
    is_vote_count_hidden.short_description = "Vote Count Hidden"

admin.site.register(Vote, VoteAdmin)
admin.site.register(AwardCategory, AwardCategoryAdmin)
