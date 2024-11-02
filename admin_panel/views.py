from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages


from user_management.models import UserProfile, Post, Comment, Like
from competition_management.models import Competition, Team, Player, Coach
from match_management.models import Match

# Create your views here.







def admin_panel(request):
    
    return render(request, 'admin/admin_base.html', )




def dashboard(request):
    return render(request, 'admin/dashboard.html')

def user_management(request):
    users = UserProfile.objects.all()

    context = {
        'users': users,
    }
    return render(request, 'admin/user_management.html', context)

def competition_management(request):
    return render(request, 'admin/competition_management.html')

def team_management(request):
    return render(request, 'admin/team_management.html')

def player_management(request):
    return render(request, 'admin/player_management.html')

def manager_coach_management(request):
    return render(request, 'admin/manager_coach_management.html')








def match_management(request):
    matches = Match.objects.all()
    return render(request, 'admin/match_management.html', {'matches': matches})

def filter_matches(request):
    competition_id = request.GET.get('competition_id')
    match_type = request.GET.get('match_type')
    
    matches = Match.objects.all()
    
    if competition_id:
        matches = matches.filter(competition_id=competition_id)
    if match_type:
        matches = matches.filter(match_type=match_type)
    
    data = [{'id': match.id, 'home_team': match.home_team.name, 'away_team': match.away_team.name, 'match_date': match.match_date.strftime('%Y-%m-%d')} for match in matches]
    
    return JsonResponse(data, safe=False)


def create_match(request):
    if request.method == 'POST':
        home_team = request.POST.get('home_team')
        away_team = request.POST.get('away_team')
        match_date = request.POST.get('match_date')
        # Assuming Match model is imported
        match = Match.objects.create(home_team=home_team, away_team=away_team, match_date=match_date)
        return redirect('match_management')  # Redirect to the match management page after creating the match
    return redirect('match_management')  # Redirect if the request method is not POST



def update_match(request, match_id):
    if request.method == 'POST':
        # Assuming Match model is imported
        match = Match.objects.get(id=match_id)
        match.home_team = request.POST.get('home_team')
        match.away_team = request.POST.get('away_team')
        match.match_date = request.POST.get('match_date')
        match.save()
        
        return JsonResponse({'success': True})  # Return a JSON response indicating success
    return JsonResponse({'success': False})  # Return a JSON response indicating failure

def delete_match(request, match_id):
    if request.method == 'POST':
        # Assuming Match model is imported
        match = Match.objects.get(id=match_id)
        match.delete()
        
        return JsonResponse({'success': True})  # Return a JSON response indicating success
    return JsonResponse({'success': False})  # Return a JSON response indicating failure







def user_list(request):
    users = UserProfile.objects.all()
    query = request.GET.get('q')
    if query:
        users = users.filter(user__username__icontains=query)
    return render(request, 'admin/user_list.html', {'users': users})


def view_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user)
    posts = Post.objects.filter(author=profile)
    comments = Comment.objects.filter(author=profile)
    likes = Like.objects.filter(user=user)
    return render(request, 'admin/view_user_partial.html', {
        'user': profile,
        'posts': posts,
        'comments': comments,
        'likes': likes
    })

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user)
    teams = Team.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        bio = request.POST.get('bio')
        favorite_team_id = request.POST.get('favorite_team')
        favorite_team = get_object_or_404(Team, id=favorite_team_id)

        user.username = username
        user.email = email
        user.save()

        profile.bio = bio
        profile.favorite_team = favorite_team
        profile.save()
        
        return redirect('user_list')
    return render(request, 'admin/edit_user_partial.html', {
        'user': profile,
        'teams': teams
    })

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'admin/delete_user_partial.html', {'user': user.profile})

def ban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.is_active = False
        user.save()
        return redirect('user_list')
    return render(request, 'admin/ban_user_partial.html', {'user': user.profile})


# def manage_user_roles(request, user_id):
#     user = get_object_or_404(User, pk=user_id)
#     if request.method == 'POST':
#         roles = request.POST.getlist('roles')
#         user.is_staff = 'admin' in roles
#         user.profile.is_coach = 'coach' in roles
#         user.profile.is_player = 'player' in roles
#         user.save()
#         user.profile.save()
#         return redirect('user_detail', user_id=user.id)
#     return render(request, 'admin/manage_user_roles.html', {'user': user})























def competition(request):
    
    competitions = Competition.objects.all()

    context = {
        'competitions': competitions,
    }
    return render(request, 'admin/competition.html', context)


def register_competition_teams(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    all_teams = Team.objects.all()
    registered_teams = competition.teams.all()

    if request.method == 'POST':
        selected_team_ids = request.POST.getlist('teams')
        for team_id in selected_team_ids:
            team = Team.objects.get(id=team_id)
            competition.teams.add(team)
        return redirect('competition', competition_id=competition.id)

    context = {
        'competition': competition,
        'all_teams': all_teams,
        'registered_teams': registered_teams,
    }
    return render(request, 'admin/register_competition_teams.html', context)




# TEAM PANEL
def team_list(request):
    teams = Team.objects.all()
    return render(request, 'admin/admin_panel.html', {'teams': teams})

def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    return render(request, 'admin/team_detail.html', {'team': team})


def create_team(request, competition_id=None):
    if request.method == 'POST':
        name = request.POST.get('name')
        logo = request.FILES.get('logo', None)
        coach_id = request.POST.get('coach')
        founded_year = request.POST.get('founded_year')

        coach = None
        if coach_id:
            try:
                coach = Coach.objects.get(pk=coach_id)
            except Coach.DoesNotExist:
                coach = None

        # Only set founded_year if provided and not empty
        if founded_year:
            founded_year = int(founded_year) if founded_year.isdigit() else None
        else:
            founded_year = None

        Team.objects.create(name=name, logo=logo, coach=coach, founded_year=founded_year)
        
        if competition_id:
            return redirect('register_competition_teams', competition_id=competition_id)
        return redirect('register_competition_teams')  # Or another relevant page if no competition_id

    else:
        coaches = Coach.objects.all()
        return render(request, 'admin/create_team.html', {'coaches': coaches, 'competition_id': competition_id})



def team_update(request, pk):
    team = get_object_or_404(Team, pk=pk)
    coaches = Coach.objects.all()

    if request.method == 'POST':
        # Update the team object with the data from the form
        team.name = request.POST.get('name')
        team.logo = request.FILES.get('logo')
        team.coach_id = request.POST.get('coach')
        team.founded_year = request.POST.get('founded_year')
        # Save the updated team object
        team.save()
        # Redirect back to the admin panel after updating
        return redirect('admin_panel')
    else:
        return render(request, 'admin/update_team.html', {'team': team, 'coaches': coaches}) 


def team_delete(request):
    if request.method == 'POST':
        team_ids = request.POST.getlist('teams')
        for team_id in team_ids:
            team = get_object_or_404(Team, pk=team_id)
            team.delete()
        return redirect('team_list')
    else:
        teams = Team.objects.all()
        return render(request, 'admin/admin_panel.html', {'teams': teams})
    


# Competition


    




def competition_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        organizer = request.POST.get('organizer')
        location = request.POST.get('location')
        description = request.POST.get('description')
        prize = request.POST.get('prize')
        registration_open = request.POST.get('registration_open') == 'on'
        logo = request.FILES.get('logo')
        # Create a new competition object
        Competition.objects.create(name=name, start_date=start_date, end_date=end_date, organizer=organizer,
                                    location=location, description=description, prize=prize,
                                    registration_open=registration_open, logo=logo)
        # Redirect back to the admin panel after creating the competition
        return redirect('admin_panel')
    else:
        # Render the admin_panel.html template with any necessary context
        return render(request, 'admin/admin_panel.html')

def competition_update(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    if request.method == 'POST':
        # Update the competition object with data from the form
        competition.name = request.POST.get('name')
        competition.start_date = request.POST.get('start_date')
        competition.end_date = request.POST.get('end_date')
        competition.organizer = request.POST.get('organizer')
        competition.location = request.POST.get('location')
        competition.description = request.POST.get('description')
        competition.prize = request.POST.get('prize')
        competition.registration_open = request.POST.get('registration_open') == 'on'
        logo = request.FILES.get('logo')
        if logo:
            competition.logo = logo
        # Save the updated competition object
        competition.save()
        # Redirect back to the admin panel after updating the competition
        return redirect('admin_panel')
    else:
        # Render the admin_panel.html template with the competition object
        return render(request, 'admin/competition_update.html', {'competition': competition})

def competition_detail(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    return render(request, 'admin/competition_detail.html', {'competition': competition})


def competition_delete(request):
    if request.method == 'POST':
        competition_ids = request.POST.getlist('competition')
        for competition_id in competition_ids:
            competition = get_object_or_404(Competition, pk=competition_id)
            competition.delete()
        return redirect('team_list')
    else:
        competitions = Competition.objects.all()
        return render(request, 'admin/admin_panel.html', {'competitions': competitions})
    



# Player
def player_list(request):
    players = Player.objects.all()
    return render(request, 'admin/player_list.html', {'players': players})

def player_detail(request, pk):
    player = get_object_or_404(Player, pk=pk)
    return render(request, 'admin/player_detail.html', {'player': player})


def player_create(request):
    if request.method == 'POST':
        # Instead of creating a new user, find the selected user
        username = request.POST.get('username')  # Assuming this is now the username or id of an existing user

        # Find the User instance based on the username
        user = get_object_or_404(User, username=username)

        # The rest remains mostly the same, except you don't create a new user
        nationality = request.POST.get('nationality')
        picture = request.FILES.get('picture')
        team_id = request.POST.get('team')
        position = request.POST.get('position')
        age = request.POST.get('age')
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        foot = request.POST.get('foot')
        biography = request.POST.get('biography')

        team = None
        if team_id:
            team = get_object_or_404(Team, pk=team_id)

        Player.objects.create(name=user, nationality=nationality, picture=picture, team=team,
                              position=position, age=age, weight=weight, height=height, foot=foot,
                              biography=biography)

        return redirect('admin_panel')
    else:
        users = User.objects.all()  # Fetch all users to select from
        return render(request, 'admin/admin_panel.html', {'users': users})
    

def player_update(request, pk):
    player = get_object_or_404(Player, pk=pk)
    teams = Team.objects.all()
    if request.method == 'POST':
        player.name = request.POST.get('name')
        player.nationality = request.POST.get('nationality')
        player.picture = request.FILES.get('picture')
        player.team_id = request.POST.get('team')
        player.position = request.POST.get('position')
        player.age = request.POST.get('age')
        player.weight = request.POST.get('weight')
        player.height = request.POST.get('height')
        player.foot = request.POST.get('foot')
        player.biography = request.POST.get('biography')
        player.save()
        return redirect('player_detail', pk=pk)
    else:
        return render(request, 'admin/player_update.html', {'player': player, 'teams': teams})
    
def player_delete(request):
    if request.method == 'POST':
        player_ids = request.POST.getlist('players')
        for player_id in player_ids:
            player = get_object_or_404(Player, pk=player_id)
            player.delete()
        return redirect('admin_panel')
    else:
        players = Player.objects.all()
        return render(request, 'admin/admin_panel.html', {'players': players})
    
