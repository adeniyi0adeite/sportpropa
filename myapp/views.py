from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate, login as authlogin, logout as authlogout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum


from django.db.models import OuterRef, Subquery, Exists, F, ExpressionWrapper, IntegerField



from .models import Feedback, SoccerNews, Contact
from user_management.models import UserProfile, Post
from fanbanter.models import FanBanterPost
from competition_management.models import Competition, Team, Player, Coach, TeamCoachCompetition, PlayerRegistration
from match_management.models import Match, PenaltyShootout, Result
from standing_management.models import Standing
from voting.models import AwardCategory, Vote

from voting.views import aggregate_votes


# from django.http import HttpResponse

# Create your views here.




def custom_404(request, exception):
    return render(request, '404.html', {}, status=404)


def index(request):
    return render(request, 'index.html')

def error404(request):
    return render(request, '404.html')


def home(request):
    competitions = Competition.objects.all()
    players = Player.objects.all()
    teams = Team.objects.all()
    news = SoccerNews.objects.all()
    user_profiles = UserProfile.objects.all()

    now = timezone.now()

    latest_competition = competitions.order_by('-created_at').first()
    
    all_categories = AwardCategory.objects.all()


    # Check if any category is open for voting
    open_categories = all_categories.filter(start_date__lte=timezone.now(), close_date__gte=timezone.now())


    player_categories = ['most_valuable_player', 'best_player', 'top_scorer', 'best_goalkeeper']
    team_categories = ['best_team']
    coach_categories = ['best_coach']

    player_categories_list = []
    team_categories_list = []
    coach_categories_list = []

    # Get total votes for players
    for cat in all_categories.filter(category__in=player_categories):
        nominees = cat.players.all()
        for nominee in nominees:
            nominee.total_votes = Vote.objects.filter(
                player=nominee, category=cat.category, competition=cat.competition
            ).aggregate(total_votes=Sum('num_of_votes'))['total_votes'] or 0
            nominee.team = PlayerRegistration.objects.filter(player=nominee, competition=cat.competition).first().team

        # Append category data to list
        player_categories_list.append({
            'category': cat,
            'nominees': nominees,
            'hide_vote_count': cat.hide_vote_count,
            'close_date': cat.close_date,  # Ensure close_date is included
            'winner': cat.winner_display(),
        })

    # Get total votes for teams
    for cat in all_categories.filter(category__in=team_categories):
        teams = cat.teams.all()
        for team in teams:
            team.total_votes = Vote.objects.filter(
                team=team, category=cat.category
            ).aggregate(total_votes=Sum('num_of_votes'))['total_votes'] or 0


        # Append category data to list
        team_categories_list.append({
            'category': cat,
            'teams': teams,
            'hide_vote_count': cat.hide_vote_count,
            'close_date': cat.close_date,  # Ensure close_date is included
            'winner': cat.winner_display(),
        })

    # Get total votes for coaches
    for cat in all_categories.filter(category__in=coach_categories):
        coaches = cat.coaches.all()
        coach_data_list = []
        for coach in coaches:
            coach.total_votes = Vote.objects.filter(
                coach=coach, category=cat.category
            ).aggregate(total_votes=Sum('num_of_votes'))['total_votes'] or 0
            
            team_coach_competition = TeamCoachCompetition.objects.filter(coach=coach, competition=cat.competition).first()

            coach_data_list.append({
                'coach': coach,
                'team': team_coach_competition.team if team_coach_competition else None,
                'total_votes': coach.total_votes,
            })

        # Append category data to list
        coach_categories_list.append({
            'category': cat,
            'coaches': coach_data_list,
            'hide_vote_count': cat.hide_vote_count,
            'close_date': cat.close_date,
            'winner': cat.get_winner() if cat.is_closed() else None,  # Call get_winner directly
            })
        
    fixtures_today = Match.objects.filter(match_date__date=now.date())

    if not fixtures_today.exists():
        fixtures_today = Match.objects.filter(match_date__gt=now).order_by('match_date')


    latest_results = Match.objects.filter(
        details__completed=True,
        match_date__lt=now
    ).select_related(
        'competition', 'details', 'home_team', 'away_team'
    ).prefetch_related(
        'goals__scorer'
    ).order_by('-match_date')

    # Dictionary to hold penalty results per match
    penalty_results = {}

    # Filter draw results
    draw_results = Result.objects.filter(
        match__in=latest_results,
        home_team_score=F('away_team_score')
    ).select_related('match').all()

    # Filter penalty shootouts associated with the draw results
    penalties = PenaltyShootout.objects.filter(result__in=draw_results, is_shootout=True)

    # Loop through draw results and assign penalty data only if penalties exist
    for result in draw_results:
        home_team_penalties = penalties.filter(result=result, team=result.match.home_team)
        away_team_penalties = penalties.filter(result=result, team=result.match.away_team)

        home_team_score = home_team_penalties.filter(is_scored=True).count()
        away_team_score = away_team_penalties.filter(is_scored=True).count()

        if home_team_penalties.exists() or away_team_penalties.exists():
            # Store the penalty data for each result if penalties exist
            penalty_results[result.match.id] = {
                'home_team_score': home_team_score,
                'away_team_score': away_team_score,
                'home_team_penalties': home_team_penalties,
                'away_team_penalties': away_team_penalties,
            }

    # Attach penalty result data directly to each match result
    for result in latest_results:
        result.penalty_data = penalty_results.get(result.id, None)


    # Attach standings, news, and other necessary data
    all_standings = {}
    for competition in competitions:
        registered_teams = competition.teams.all()

        if competition.is_group_stage:
            groups = competition.groups.all()
            first_group = groups.first()
            standings = {}
            for group in groups:
                group_teams = group.teams.filter(id__in=registered_teams.values_list('id', flat=True))
                group_standings = Standing.objects.filter(competition=competition, group=group, team__in=group_teams)
                standings[group] = group_standings.prefetch_related('team').order_by('-points', '-goals_for')

            all_standings[competition] = {
                'standings': standings,
                'first_group': first_group,
            }
        else:
            standings = Standing.objects.filter(competition=competition, team__in=registered_teams).prefetch_related('team').order_by('-points', '-goals_for')
            all_standings[competition] = standings

    posts = []
    if request.user.is_authenticated:
        posts = Post.objects.prefetch_related(
            'comments__author',
            'comments__replies__author',
            'comments__replies__likes',
            'comments__likes',
            'likes'
        ).order_by('-created_at')

        for post in posts:
            post.num_likes = post.likes.count()
            post.user_has_liked = post.likes.filter(user=request.user).exists()
            post.num_comments = post.comments.filter(parent__isnull=True).count()

            for comment in post.comments.all():
                comment.num_likes = comment.likes.count()
                comment.user_has_liked = comment.likes.filter(user=request.user).exists()

                for reply in comment.replies.all():
                    reply.num_likes = reply.likes.count()
                    reply.user_has_liked = reply.likes.filter(user=request.user).exists()

    context = {
        'competitions': competitions,
        'players': players,
        'teams': teams,
        'latest_results': latest_results,
        'penalty_results': penalty_results,
        'all_standings': all_standings,
        'latest_competition': latest_competition,
        'news': news,
        'posts': posts,
        'fixtures_today': fixtures_today,
        'user_profiles': user_profiles,
        'player_categories': player_categories_list,
        'team_categories': team_categories_list,
        'coach_categories': coach_categories_list,
        'open_categories': open_categories.exists(),  # Check if there are open categories

    }

    return render(request, 'home.html', context)


@login_required(login_url='loginform')
def user_posts(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.user.is_authenticated:
        # Subquery to check if the post author is followed by the current user
        following_subquery = UserProfile.objects.filter(
            user=OuterRef('author'),
            followers=user_profile
        ).values('pk')

        posts = Post.objects.annotate(
            is_followed=Exists(following_subquery)
        ).prefetch_related(
            'comments__author',
            'comments__replies__author',
            'comments__replies__likes',
            'comments__likes',
            'likes',
            'author__followers'
        ).order_by('-is_followed', '-created_at')

        for post in posts:
            post.is_followed = post.author.user.profile.is_followed_by(request.user)
            post.num_likes = post.likes.count()
            post.user_has_liked = post.likes.filter(user=request.user).exists()
            post.num_comments = post.comments.filter(parent__isnull=True).count()

            for comment in post.comments.all():
                comment.num_likes = comment.likes.count()
                comment.user_has_liked = comment.likes.filter(user=request.user).exists()

                for reply in comment.replies.all():
                    reply.num_likes = reply.likes.count()
                    reply.user_has_liked = reply.likes.filter(user=request.user).exists()

    else:
        posts = Post.objects.all().prefetch_related(
            'comments__author',
            'comments__replies__author',
            'comments__replies__likes',
            'comments__likes',
            'likes',
            'author__followers'
        ).order_by('-created_at')

    context = {
        'posts': posts,
    }

    return render(request, 'user_posts.html', context)



def news(request):
    news = SoccerNews.objects.all().order_by('-published_date')[:10]
    return render(request, 'news.html', {'news': news})  
    


def about_us(request):
    
    return render(request, 'about_us.html')


def feedback(request):
    feedbacks = Feedback.objects.all().order_by('-submitted_on')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        feedback_type = request.POST.get('feedbackType')
        message = request.POST.get('message')
        experience_rating = request.POST.get('experienceRating')
        suggestions = request.POST.get('suggestions', '')  # Optional field

        if not all([name, email, feedback_type, message, experience_rating]):
            return JsonResponse({
                'success': False,
                'error': 'Please fill out all required fields.'
            }, status=400)

        feedback = Feedback(
            name=name,
            email=email,
            feedback_type=feedback_type,
            message=message,
            experience_rating=experience_rating,
            suggestions=suggestions,
            submitted_on=timezone.now()
        )
        feedback.save()
        return JsonResponse({
            'success': True,
            'message': 'Your feedback has been submitted successfully.',
        })

    return render(request, 'feedback.html', {'feedbacks': feedbacks})


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        email = request.POST.get('email')

        if not all([name, phone, message, email]):
            return JsonResponse({
                'success': False,
                'error': 'Please fill out all required fields.'
            }, status=400)

        Contact.objects.create(name=name, phone=phone, message=message, email=email)
        return JsonResponse({'success': True, 'message': 'Your message has been submitted successfully.',})
    return render(request, 'contact.html')




@login_required(login_url='loginform')
def search_users(request):
    query = request.GET.get('q', '')  # Get the query from the request
    results = []

    if query:
        search_results = UserProfile.objects.filter(user__username__icontains=query)
        for profile in search_results:
            is_followed = request.user.profile.following.filter(id=profile.user.profile.id).exists()
            results.append({'profile': profile, 'is_followed': is_followed})

    return render(request, 'search_users.html', {'results': results, 'query': query})