from competition_management.models import Competition, Team, Player



def add_variable_to_context(request):
    return {
        'competitions': Competition.objects.all(),
        'teams': Team.objects.all(),
        'players': Player.objects.all(),
    }