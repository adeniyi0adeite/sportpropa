from django.shortcuts import render, redirect, get_object_or_404

from django.core.validators import validate_email

from django.contrib.auth import authenticate, login as authlogin, logout as authlogout
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q, F, Subquery, OuterRef, Value, Case, When, ExpressionWrapper, IntegerField
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.core.files.storage import default_storage
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from collections import defaultdict


import os
from PIL import Image, ImageFile
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile




from .models import Competition, CupGroup, Team, Player, PlayerRegistration, PlayerPost, CompetitionComment, CompetitionLike, TeamComment, TeamLike, PlayerComment, PlayerLike
from match_management.models import Result, Match, MatchStatistic, Goal, Save, Card, PenaltyShootout
from standing_management.models import Standing
from user_management.models import UserProfile
from voting.models import AwardCategory
from myapp.models import Award

# from django.http import HttpResponse

# Create your views here.



# SPORT VIEW
# @login_required(login_url='loginform')

def player(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    target_player = player.name

    registrations = PlayerRegistration.objects.filter(player=player)

    # Get all results where this player is the man of the match
    man_of_the_match_results = Result.objects.filter(man_of_the_match=player)
    
    # Calculate the total number of man of the match awards
    total_man_of_the_match_awards = man_of_the_match_results.count()
    
    # Get all awards where the player is a nominee (in the players field)
    awards = AwardCategory.objects.filter(players=player)
    player_awards = []

    for award in awards:
        # Check if voting is closed before checking for a winner
        if not award.is_voting_active():
            winner = award.get_winner()
            if winner == player:
                player_awards.append(award)


    # Calculate total awards won
    total_awards_won = len(player_awards)

    total_goals = Goal.objects.filter(scorer=player, is_own_goal=False).count()
    total_own_goals = Goal.objects.filter(scorer=player, is_own_goal=True).count()
    total_assists = Goal.objects.filter(assist=player).count()
    total_yellow_cards = Card.objects.filter(player=player, card_type=Card.YELLOW).count()
    total_red_cards = Card.objects.filter(player=player, card_type=Card.RED).count()

    # Initialize goalkeeper stats
    total_saves = 0
    clean_sheets = 0

    # Only calculate saves and clean sheets for goalkeepers
    if player.position == player.GOALKEEPER:
        # Calculate total saves
        total_saves = Save.objects.filter(goalkeeper=player).count()

        # Get matches where the player played as a goalkeeper
        player_matches = Match.objects.filter(
            Q(home_team__players=player) | Q(away_team__players=player)
        ).distinct()

        # Calculate clean sheets based on match results
        for match in player_matches:
            result = Result.objects.filter(match=match).first()

            if result:
                # Determine if the player was the home or away goalkeeper
                if match.home_team.players.filter(id=player.id).exists():
                    if result.away_team_score == 0:
                        clean_sheets += 1
                elif match.away_team.players.filter(id=player.id).exists():
                    if result.home_team_score == 0:
                        clean_sheets += 1



    # Pagination setup for images and videos
    media_posts = PlayerPost.objects.filter(player=player).order_by('-uploaded_at')
    paginator = Paginator(media_posts, 6)  # Show 6 posts per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    is_owner = request.user.is_authenticated and request.user == target_player

    login_user_profile = None
    comments = None
    num_comments = None
    num_likes = None

    if request.user.is_authenticated:
        login_user_profile = UserProfile.objects.get(user=request.user)
        # Prefetch related data for comments, replies, and likes
        prefetch_queries = [
            'player_comments__player_replies',
            'player_comments__player_likes',
            'player_comments__player_replies__player_likes',
            'player_likes'
        ]

        # Fetch the competition object with prefetched related data
        player = get_object_or_404(Player.objects.prefetch_related(*prefetch_queries), name=target_player)
        
        # Get all top-level comments for this competition
        comments = player.player_comments.filter(parent__isnull=True)

        # Calculate the number of top-level comments for the competition
        num_comments = comments.count()
        
        # Calculate the number of likes for the competition
        num_likes = player.player_likes.count()
        # Check if the user has liked the competition
        player.user_has_liked = player.player_likes.filter(user=request.user.profile).exists()
        
        # Iterate over top-level comments to calculate likes for each comment and its replies
        for comment in player.player_comments.all():
            comment.num_likes = comment.player_likes.count()
            comment.user_has_liked = comment.player_likes.filter(user=request.user.profile).exists()
            comment.num_replies = comment.player_replies.count()

            for reply in comment.player_replies.all():
                reply.num_likes = reply.player_likes.count()
                reply.user_has_liked = reply.player_likes.filter(user=request.user.profile).exists()

    context = {
        'player': player,
        'total_goals': total_goals,
        'total_own_goals': total_own_goals,
        'total_assists': total_assists,
        'total_yellow_cards': total_yellow_cards,
        'total_red_cards': total_red_cards,
        'is_owner': is_owner,
        'total_saves': total_saves,
        'clean_sheets': clean_sheets,

        'man_of_the_match_results': man_of_the_match_results,
        'total_man_of_the_match_awards': total_man_of_the_match_awards,
        'player_awards': player_awards,
        'total_awards_won': total_awards_won,

        'page_obj': page_obj,
        'login_user': login_user_profile,
        'comments': comments,
        'num_comments': num_comments,
        'num_likes': num_likes,
        'registrations': registrations,

    }
    return render(request, 'player.html', context)




@login_required(login_url='loginform')
def player_comment(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    if request.method == "POST" and request.POST.get('message'):
        comment_text = request.POST.get('message')
        parent_id = request.POST.get('parent_id', None)
        try:
            if parent_id:
                parent_comment = PlayerComment.objects.get(id=parent_id)
                comment = PlayerComment.objects.create(
                    player=player,
                    author=request.user.profile,
                    content=comment_text,
                    parent=parent_comment
                )
            else:
                comment = PlayerComment.objects.create(
                    player=player,
                    author=request.user.profile,
                    content=comment_text
                )
            messages.success(request, "Comment successfully posted.")
        except PlayerComment.DoesNotExist:
            messages.error(request, 'Parent comment not found.')
        return redirect('player', player_name=player.name)

    # If it's not a POST request or no message provided, render competition page
    return redirect('player', player_name=player.name)



@login_required(login_url='loginform')
def toggle_player_like(request, player_id=None, comment_id=None):
    user = request.user.profile
    if request.method == 'POST':
        item = None
        model_type = None

        if player_id:
            item = get_object_or_404(Player, id=player_id)
            model_type = 'player'
        elif comment_id:
            item = get_object_or_404(PlayerComment, id=comment_id)
            model_type = 'comment'

        if not item:
            return JsonResponse({'success': False, 'error': 'Invalid like toggle request'}, status=400)

        filter_kwargs = {'user': user}
        filter_kwargs[model_type] = item
        liked = PlayerLike.objects.filter(**filter_kwargs).exists()

        if liked:
            PlayerLike.objects.filter(**filter_kwargs).delete()
            liked = False
        else:
            PlayerLike.objects.create(**filter_kwargs)
            liked = True

        # num_likes = item.competition_likes.count()

        # Count the likes using the correct related_name
        if model_type == 'player':
            num_likes = item.player_likes.count()
        elif model_type == 'comment':
            num_likes = item.player_likes.count()

        return JsonResponse({'success': True, 'liked': liked, 'num_likes': num_likes})
    else:
        return JsonResponse({'success': False, 'error': 'This request requires POST method.'}, status=400)




@login_required(login_url='loginform')
def delete_player_comment(request, comment_id):
    comment = get_object_or_404(PlayerComment, id=comment_id)
    
    if request.user.profile == comment.author:
        comment.delete()
        messages.success(request, "Comment successfully deleted.")
    else:
        messages.error(request, "You do not have permission to delete this comment.")
    
    return redirect('player', player_name=comment.player.name)





@login_required(login_url='loginform')
def edit_player_info(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    if request.method == 'POST':
        # Update user information
        user = player.name
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()

        # Update player information
        player.nationality = request.POST.get('nationality')
        player.position = request.POST.get('position')
        player.age = request.POST.get('age')
        player.height = request.POST.get('height')
        player.weight = request.POST.get('weight')
        player.foot = request.POST.get('foot')
        player.biography = request.POST.get('biography')
        player.save()

        return redirect('player', player_name=username)
    else:
        return render(request, 'player.html', {'player': player})



@login_required(login_url='loginform')
def change_player_picture(request, player_id):
    
    if request.method == 'POST':
        try:
            player_profile = get_object_or_404(Player, id=player_id)
            # If there's an existing picture, delete it before saving the new one
            if player_profile.picture and default_storage.exists(player_profile.picture.name):
                default_storage.delete(player_profile.picture.name)
            # Replace with new picture from the form
            player_profile.picture = request.FILES['new_picture']
            player_profile.save()
            # Redirect to the profile page
            return redirect('player', player_id=player_profile.id)
        except Player.DoesNotExist:
            pass  # Handle error or redirect as appropriate
    return redirect('player', player_id=player_profile.id)



# Allowed extensions without leading dots
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

def validate_file(file):
    ext = os.path.splitext(file.name)[1].lower().lstrip('.')

    if ext in ALLOWED_IMAGE_EXTENSIONS:
        file_type = 'image'
        allowed_extensions = ALLOWED_IMAGE_EXTENSIONS
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        file_type = 'video'
        allowed_extensions = ALLOWED_VIDEO_EXTENSIONS
    else:
        raise ValidationError("Unsupported file type.")

    extension_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
    try:
        extension_validator(file)
    except ValidationError as e:
        raise ValidationError(f"Invalid file type: {e}")

    if file.size > MAX_FILE_SIZE:
        raise ValidationError(f"File size exceeds the maximum limit of {MAX_FILE_SIZE // (1024 * 1024)} MB.")

    if file_type == 'image':
        try:
            img = Image.open(file)
            img.verify()  # Verifies that it is an actual image
        except Exception as e:
            raise ValidationError(f"Invalid image file: {e}")
    
    # Skip detailed validation for videos since Pillow can't handle it
    if file_type == 'video':
        pass  # Basic checks like extension and size have already been done

    return file_type


def upload_player_post(request, player_id):
    if request.method == 'POST':
        player = get_object_or_404(Player, id=player_id)
        files = request.FILES.getlist('media')
        caption = request.POST.get('caption', '').strip()
        
        for file in files:
            try:
                file_type = validate_file(file)

                if file_type == 'image':
                    PlayerPost.objects.create(player=player, image=file, caption=caption)
                elif file_type == 'video':
                    PlayerPost.objects.create(player=player, video=file, caption=caption)

                messages.success(request, "Successfully uploaded.")
            except ValidationError as e:
                messages.error(request, f"Failed to upload: {e}")

        return redirect('player', player_name=player.name.username)
    
    return redirect('player')




def load_more_posts(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    offset = int(request.GET.get('offset', 0))
    limit = 3
    posts = PlayerPost.objects.filter(player=player).order_by('-uploaded_at')[offset:offset+limit]
    
    post_data = []
    for post in posts:
        if post.image:
            post_data.append({'type': 'image', 'url': post.image.url, 'name': post.image.name})
        if post.video:
            post_data.append({'type': 'video', 'url': post.video.url, 'name': post.video.name})
    
    return JsonResponse({'posts': post_data})


def competition(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    
    # Fetch matches and related results, optimizing queries
    matches = Match.objects.filter(competition=competition).order_by('match_date').select_related(
        'home_team', 'away_team', 'group',
    ).prefetch_related(
        'goals', 'goals__scorer', 'goals__scoring_team', 'details__penalties__player'
    )
    
    current_time = timezone.now()
    
    # Fetch completed matches
    results = Match.objects.filter(
        competition=competition,
        match_date__lt=current_time,
        details__completed=True
    ).select_related(
        'competition', 'details', 'home_team', 'away_team'
    ).prefetch_related(
        'goals__scorer', 'details__penalties__player'
    ).order_by('-match_date')

    

    # Dictionary to hold penalty results per match
    penalty_results = {}

    # Filter draw results
    draw_results = Result.objects.filter(
        match__in=results,
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
    for result in results:
        result.penalty_data = penalty_results.get(result.id, None)


    
    # Fetch upcoming fixtures
    fixtures = matches.filter(match_date__gte=current_time).order_by('match_date')
    
    # Get the current number of fixtures to display, default to 3
    num_fixtures = request.GET.get('num_fixtures', 3)
    num_fixtures = int(num_fixtures)
    
    # Create paginator for upcoming fixtures
    paginator = Paginator(fixtures, num_fixtures)
    page_number = request.GET.get('page', 1)  # Get the page number from the request
    page_obj = paginator.get_page(page_number)

    past_matches = matches.filter(match_date__lt=current_time)
    next_fixture = fixtures.first()

    registered_teams = competition.teams.all()

    # Fetch player goals and assists
    player_goals = {}
    player_assists = {}
    
    player_values = (
        'scorer__id',
        'scorer__name__username',
        'scorer__name__first_name', 
        'scorer__name__last_name', 
        'scoring_team__name'
    )
    assist_values = (
        'assist__id',
        'assist__name__username',
        'assist__name__first_name', 
        'assist__name__last_name', 
        'assist__registrations__team__name'
    )

    if competition.is_school_competition:
        player_goals['School'] = Goal.objects.filter(
            match__in=matches, 
            match__competition__is_school_competition=True,
            scorer__registrations__competition=competition,
            is_own_goal=False
        ).values(*player_values).annotate(total_goals=Count('id', distinct=True)).order_by('-total_goals')

        player_assists['School'] = Goal.objects.filter(
            match__in=matches, 
            match__competition__is_school_competition=True,
            assist__isnull=False,
            assist__registrations__competition=competition,
            is_own_goal=False
        ).values(*assist_values).annotate(total_assists=Count('id', distinct=True)).order_by('-total_assists')
    else:
        if competition.competition_type == Competition.LEAGUE:
            player_goals['League'] = Goal.objects.filter(
                match__in=matches, 
                match__competition__competition_type=Competition.LEAGUE,
                scorer__registrations__competition=competition,
                is_own_goal=False
            ).values(*player_values).annotate(total_goals=Count('id', distinct=True)).order_by('-total_goals')

            player_assists['League'] = Goal.objects.filter(
                match__in=matches, 
                match__competition__competition_type=Competition.LEAGUE,
                assist__isnull=False,
                assist__registrations__competition=competition,
                is_own_goal=False
            ).values(*assist_values).annotate(total_assists=Count('id', distinct=True)).order_by('-total_assists')

        elif competition.competition_type == Competition.CUP:
            player_goals['Cup'] = Goal.objects.filter(
                match__in=matches, 
                match__competition__competition_type=Competition.CUP,
                scorer__registrations__competition=competition,
                is_own_goal=False
            ).values(*player_values).annotate(total_goals=Count('id', distinct=True)).order_by('-total_goals')

            player_assists['Cup'] = Goal.objects.filter(
                match__in=matches, 
                match__competition__competition_type=Competition.CUP,
                assist__isnull=False,
                assist__registrations__competition=competition,
                is_own_goal=False
            ).values(*assist_values).annotate(total_assists=Count('id', distinct=True)).order_by('-total_assists')

    groups = None
    standings = None
    first_group = None
    if competition.is_group_stage:
        groups = competition.groups.all()
        first_group = groups.first() if groups.exists() else None
        standings = {}
        for group in groups:
            group_teams = group.teams.filter(id__in=registered_teams.values_list('id', flat=True))
            group_standings = Standing.objects.filter(competition=competition, group=group, team__in=group_teams)
            standings[group] = group_standings.prefetch_related('team').order_by('-points', '-goals_for')

            missing_teams = group_teams.exclude(id__in=group_standings.values_list('team__id', flat=True))
            for team in missing_teams:
                Standing.objects.create(competition=competition, group=group, team=team)
    else:
        standings = Standing.objects.filter(competition=competition, team__in=registered_teams).prefetch_related('team').order_by('-points', '-goals_for')
        missing_teams = registered_teams.exclude(id__in=standings.values_list('team__id', flat=True))
        for team in missing_teams:
            Standing.objects.create(competition=competition, team=team)



    login_user_profile = None
    comments = None
    num_comments = None
    num_likes = None

    if request.user.is_authenticated:
        login_user_profile = UserProfile.objects.get(user=request.user)
        prefetch_queries = [
            'competition_comments__competition_replies',
            'competition_comments__competition_likes',
            'competition_comments__competition_replies__competition_likes',
            'competition_likes'
        ]
        competition = get_object_or_404(Competition.objects.prefetch_related(*prefetch_queries), id=competition_id)
        comments = competition.competition_comments.filter(parent__isnull=True)
        num_comments = comments.count()
        num_likes = competition.competition_likes.count()
        competition.user_has_liked = competition.competition_likes.filter(user=request.user.profile).exists()

        for comment in competition.competition_comments.all():
            comment.num_likes = comment.competition_likes.count()
            comment.user_has_liked = comment.competition_likes.filter(user=request.user.profile).exists()
            comment.num_replies = comment.competition_replies.count()

            for reply in comment.competition_replies.all():
                reply.num_likes = reply.competition_likes.count()
                reply.user_has_liked = reply.competition_likes.filter(user=request.user.profile).exists()




    context = {
        'competition': competition,
        'registered_teams': registered_teams,
        'standings': standings,
        'first_group': first_group,
        'matches': matches,
        'results': results,
        'penalty_results': penalty_results,
        'fixtures': fixtures,
        'past_matches': past_matches,
        'next_fixture': next_fixture,
        'groups': groups,
        'player_goals': player_goals,
        'player_assists': player_assists,
        'page_obj': page_obj,
        'num_fixtures': num_fixtures,
        'login_user': login_user_profile,
        'comments': comments,
        'num_comments': num_comments,
        'num_likes': num_likes
    }

    return render(request, 'competition.html', context)



def competition_info(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    matches = Match.objects.filter(competition=competition).order_by('match_date')
    results = Result.objects.filter(match__in=matches, completed=True).order_by('-match__match_date')

    fixtures = matches.filter(match_date__gte=timezone.now()).order_by('match_date')
    registered_teams = competition.teams.all()

    groups = None
    standings = None
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
    else:
        standings = Standing.objects.filter(competition=competition, team__in=registered_teams).prefetch_related('team').order_by('-points', '-goals_for')
        missing_teams = registered_teams.exclude(id__in=standings.values_list('team__id', flat=True))
        for team in missing_teams:
            Standing.objects.create(competition=competition, team=team)

    context = {
        'competition': competition,
        'registered_teams': registered_teams,
        'standings': standings,
        'matches': matches,
        'results': results,
        'fixtures': fixtures,
        'groups': groups,
        

    }
    
    return render(request, 'competition_info.html', context)


@login_required(login_url='loginform')
def competition_comment(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)

    if request.method == "POST" and request.POST.get('message'):
        comment_text = request.POST.get('message')
        parent_id = request.POST.get('parent_id', None)
        try:
            if parent_id:
                parent_comment = CompetitionComment.objects.get(id=parent_id)
                comment = CompetitionComment.objects.create(
                    competition=competition,
                    author=request.user.profile,
                    content=comment_text,
                    parent=parent_comment
                )
            else:
                comment = CompetitionComment.objects.create(
                    competition=competition,
                    author=request.user.profile,
                    content=comment_text
                )
            messages.success(request, "Comment successfully posted.")
        except CompetitionComment.DoesNotExist:
            messages.error(request, 'Parent comment not found.')
        return redirect('competition', competition_id=competition.id)

    # If it's not a POST request or no message provided, render competition page
    return redirect('competition', competition_id=competition.id)


@login_required(login_url='loginform')
def toggle_competition_like(request, competition_id=None, comment_id=None):
    user = request.user.profile
    if request.method == 'POST':
        item = None
        model_type = None

        if competition_id:
            item = get_object_or_404(Competition, id=competition_id)
            model_type = 'competition'
        elif comment_id:
            item = get_object_or_404(CompetitionComment, id=comment_id)
            model_type = 'comment'

        if not item:
            return JsonResponse({'success': False, 'error': 'Invalid like toggle request'}, status=400)

        filter_kwargs = {'user': user}
        filter_kwargs[model_type] = item
        liked = CompetitionLike.objects.filter(**filter_kwargs).exists()

        if liked:
            CompetitionLike.objects.filter(**filter_kwargs).delete()
            liked = False
        else:
            CompetitionLike.objects.create(**filter_kwargs)
            liked = True

        # num_likes = item.competition_likes.count()

        # Count the likes using the correct related_name
        if model_type == 'competition':
            num_likes = item.competition_likes.count()
        elif model_type == 'comment':
            num_likes = item.competition_likes.count()

        return JsonResponse({'success': True, 'liked': liked, 'num_likes': num_likes})
    else:
        return JsonResponse({'success': False, 'error': 'This request requires POST method.'}, status=400)


@login_required(login_url='loginform')
def delete_competition_comment(request, comment_id):
    comment = get_object_or_404(CompetitionComment, id=comment_id)
    
    if request.user.profile == comment.author:
        comment.delete()
        messages.success(request, "Comment successfully deleted.")
    else:
        messages.error(request, "You do not have permission to delete this comment.")
    
    return redirect('competition', competition_name=comment.competition.name)



def load_more_fixtures(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    matches = Match.objects.filter(competition=competition).order_by('match_date')
    fixtures = matches.filter(match_date__gte=timezone.now()).order_by('match_date')

    paginator = Paginator(fixtures, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    fixtures_html = render_to_string('fixtures_list.html', {'page_obj': page_obj})
    return JsonResponse({'fixtures_html': fixtures_html})



def team(request, team_id):
    team = get_object_or_404(Team, id=team_id)



    current_time = timezone.now()
    awards = Award.objects.filter(team=team)


    # Subquery to get the latest competition registration for each player
    latest_registration_subquery = PlayerRegistration.objects.filter(
        player=OuterRef('player')
    ).order_by('-competition__created_at').values('id')[:1]

    # Main query to get the latest player registrations
    latest_player_registrations = PlayerRegistration.objects.filter(
        id__in=Subquery(latest_registration_subquery)
    ).select_related('player', 'competition', 'team')

    # Get all registrations for the specified team
    player_registrations = PlayerRegistration.objects.filter(
        team=team
    ).select_related('player', 'competition', 'team')

    # Create a list of player IDs who have their latest registration with the specified team
    current_player_ids = [registration.player.id for registration in latest_player_registrations if registration.team.id == team.id]

    # Mark players who are not currently registered with the specified team
    for registration in player_registrations:
        registration.is_latest_team = registration.player.id in current_player_ids

    # Sort registrations to have current players first
    player_registrations = sorted(player_registrations, key=lambda reg: not reg.is_latest_team)

    # Filter competitions associated with the team and where registration is open
    register_player_to_competition = Competition.objects.filter(teams=team, registration_open=True)

    # Fetch competitions with related groups and standings preloaded
    competitions = team.competitions.prefetch_related('groups', 'standings').all()

    # Assuming `competitions` is a queryset of your competitions
    latest_competition = competitions.order_by('-created_at').first()
    
    cup_standings = []
    league_standings = []
    for comp in competitions:
        if comp.competition_type == Competition.CUP and comp.is_group_stage:
            group = comp.groups.filter(teams=team).first()
            if group:
                group_teams = group.teams.all()
                comp_standings = comp.standings.filter(group=group, team__in=group_teams).order_by('-points', '-goals_for')
                missing_teams = group_teams.exclude(id__in=comp_standings.values_list('team', flat=True))
                for missing_team in missing_teams:
                    comp.standings.get_or_create(group=group, team=missing_team, defaults={'points': 0})
                cup_standings.append({'competition': comp, 'group': group, 'standings': comp_standings})
        else:
            comp_standings = comp.standings.filter(team__in=comp.teams.all()).order_by('-points')
            league_standings.append({'competition': comp, 'standings': comp_standings})

    
    
    fixtures = Match.objects.filter(Q(home_team=team) | Q(away_team=team), match_date__gte=current_time).order_by('match_date')
    
    next_fixture = fixtures.first()

    # Optimize with select_related and prefetch_related
    results = Match.objects.filter(
        Q(home_team=team) | Q(away_team=team),
        match_date__lt=current_time,
        details__completed=True
    ).select_related(
        'competition', 'details', 'home_team', 'away_team'
    ).prefetch_related(
        'goals__scorer'  # Prefetch related goals and scorer data
    ).order_by('-match_date')

    # Dictionary to hold penalty results per match
    penalty_results = {}

    # Filter matches that ended in a draw
    draw_results = Result.objects.filter(
        match__in=results,
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
    for result in results:
        result.penalty_data = penalty_results.get(result.id, None)


    # Calculate clean sheets
    clean_sheets = Result.objects.filter(
        Q(match__home_team=team, away_team_score=0) |
        Q(match__away_team=team, home_team_score=0)
    ).count()

    # Calculate wins, losses, and draws
    wins = Result.objects.filter(
        Q(match__home_team=team, home_team_score__gt=F('away_team_score')) |
        Q(match__away_team=team, away_team_score__gt=F('home_team_score'))
    ).count()

    losses = Result.objects.filter(
        Q(match__home_team=team, home_team_score__lt=F('away_team_score')) |
        Q(match__away_team=team, away_team_score__lt=F('home_team_score'))
    ).count()

    draws = Result.objects.filter(
        Q(match__home_team=team, home_team_score=F('away_team_score')) |
        Q(match__away_team=team, away_team_score=F('home_team_score'))
    ).count()


    # Calculate goals scored
    goals_scored_regular = Goal.objects.filter(scoring_team=team, is_own_goal=False).count()
    goals_scored_own_goals_by_opponents_as_home = Goal.objects.filter(match__home_team=team, is_own_goal=True).exclude(scoring_team=team).count()
    goals_scored_own_goals_by_opponents_as_away = Goal.objects.filter(match__away_team=team, is_own_goal=True).exclude(scoring_team=team).count()
    
    goals_scored = goals_scored_regular + goals_scored_own_goals_by_opponents_as_home + goals_scored_own_goals_by_opponents_as_away
    
    # Calculate goals conceded
    goals_conceded_as_scoring_team = Goal.objects.filter(scoring_team=team, is_own_goal=True).count()
    goals_conceded_as_opponent = Goal.objects.filter(match__home_team=team, is_own_goal=False).exclude(scoring_team=team).count()
    goals_conceded_as_opponent += Goal.objects.filter(match__away_team=team, is_own_goal=False).exclude(scoring_team=team).count()
    
    goals_conceded = goals_conceded_as_scoring_team + goals_conceded_as_opponent
    

    
    # Calculate yellow and red cards distinctly for the team
    yellow_cards = Card.objects.filter(
        card_type=Card.YELLOW,
        match__competition__in=competitions,
        player__registrations__team=team,
        player__registrations__competition=F('match__competition')
    ).distinct().count()

    red_cards = Card.objects.filter(
        card_type=Card.RED,
        match__competition__in=competitions,
        player__registrations__team=team,
        player__registrations__competition=F('match__competition')
    ).distinct().count()


    # Player statistics
    total_goals = Goal.objects.filter(scoring_team=team).count()
    total_assists = Goal.objects.filter(assist__registrations__team=team).count()
    

    # Rankings for goals, filtering by team and specific competition
    goal_ranking = Goal.objects.filter(scoring_team=team, is_own_goal=False) \
        .select_related('match', 'match__competition') \
        .values('scorer__id', 'scorer__name__username', 'scorer__name__first_name', 'scorer__name__last_name', 'match__competition__id') \
        .annotate(total_goals=Count('id')) \
        .filter(match__competition__teams=team) \
        .order_by('-total_goals')

    # Rankings for assists, filtering by the team for which the assist was made in a specific competition
    assist_ranking = Goal.objects.filter(scoring_team=team, assist__isnull=False, is_own_goal=False) \
        .select_related('match', 'match__competition', 'assist', 'scoring_team') \
        .values('assist__id', 'assist__name__username', 'assist__name__first_name', 'assist__name__last_name', 'match__competition__id') \
        .annotate(total_assists=Count('id')) \
        .filter(match__competition__teams=team) \
        .order_by('-total_assists')

    player_positions = Player.PLAYER_POSITIONS



    login_user_profile = None
    comments = None
    num_comments = None
    num_likes = None
    if request.user.is_authenticated:

        login_user_profile = UserProfile.objects.get(user=request.user)
        # Prefetch related data for comments, replies, and likes
        prefetch_queries = [
            'team_comments__team_replies',
            'team_comments__team_likes',
            'team_comments__team_replies__team_likes',
            'team_likes'
        ]

        # Fetch the competition object with prefetched related data
        team = get_object_or_404(Team.objects.prefetch_related(*prefetch_queries), id=team.id)
        


        # Get all top-level comments for this team
        comments = team.team_comments.filter(parent__isnull=True)
        
        # Calculate the number of top-level comments for the competition
        num_comments = comments.count()
        
        # Calculate the number of likes for the competition
        num_likes = team.team_likes.count()
        # Check if the user has liked the competition
        team.user_has_liked = team.team_likes.filter(user=request.user.profile).exists()
        
        # Iterate over top-level comments to calculate likes for each comment and its replies
        for comment in team.team_comments.all():
            comment.num_likes = comment.team_likes.count()
            comment.user_has_liked = comment.team_likes.filter(user=request.user.profile).exists()
            comment.num_replies = comment.team_replies.count()

            for reply in comment.team_replies.all():
                reply.num_likes = reply.team_likes.count()
                reply.user_has_liked = reply.team_likes.filter(user=request.user.profile).exists()

    context = {
        'team': team,
        'competition': competition,
        # 'players': players,
        'player_positions': player_positions,
        'latest_competition': latest_competition,
        'cup_standings': cup_standings,
        'league_standings': league_standings,
        'fixtures': fixtures,
        'next_fixture': next_fixture,
        'results': results,
        'total_goals': total_goals,
        'total_assists': total_assists,
        'goal_ranking': goal_ranking,
        'assist_ranking': assist_ranking,
        'clean_sheets': clean_sheets,
        'wins': wins,
        'losses': losses,
        'draws': draws,
        'goals_scored': goals_scored,
        'goals_conceded': goals_conceded,
        'yellow_cards': yellow_cards,
        'red_cards': red_cards,
        'awards': awards,
        'player_registrations': player_registrations,
        'register_player_to_competition': register_player_to_competition,


        'login_user': login_user_profile,
        'comments': comments,
        'num_comments': num_comments,
        'num_likes': num_likes,
        
        'penalty_results': penalty_results,
        
    }
    return render(request, 'team.html', context)
    


def add_player_to_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if request.method == 'POST':
        competition_id = request.POST.get('competition')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        position = request.POST.get('position')
        
        # Ensure required fields are provided
        if not all([competition_id, first_name, last_name, username, position,]):
            messages.error(request, 'Please provide all required fields.')
            return redirect('team', team_id=team.id)

        # Retrieve the Competition instance
        competition = get_object_or_404(Competition, id=competition_id)
        
        # Retrieve optional fields
        nationality = request.POST.get('nationality', 'N/A')
        picture = request.FILES.get('picture', '')
        foot = request.POST.get('foot', '')
        
        # Convert age and other numeric fields to appropriate types
        try:
            age = int(request.POST.get('age', ''))
        except ValueError:
            age = None  # or set to default value if needed

        try:
            weight = float(request.POST.get('weight', ''))
        except ValueError:
            weight = None  # or set to default value if needed

        try:
            height = float(request.POST.get('height', ''))
        except ValueError:
            height = None  # or set to default value if needed

        biography = request.POST.get('biography', '')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'The username already exists. Please choose a different username.')
            return redirect('team', team_id=team.id)

        # Create user
        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=request.POST.get('email', '')  # Optional field
        )

        # Create player
        player = Player.objects.create(
            name=user,
            nationality=nationality,
            picture=picture,
            team=team,
            position=position,
            age=age,
            weight=weight,
            height=height,
            foot=foot,
            biography=biography
        )

        # Register player in the team for the competition
        PlayerRegistration.objects.create(
            player=player,
            team=team,
            competition=competition,
        )

        messages.success(request, 'Player added successfully.')
        return redirect('team', team_id=team.id)

    return render(request, 'team.html', {'team': team})


@login_required(login_url='loginform')
def team_comment(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if request.method == "POST" and request.POST.get('message'):
        comment_text = request.POST.get('message')
        parent_id = request.POST.get('parent_id', None)
        try:
            if parent_id:
                parent_comment = TeamComment.objects.get(id=parent_id)
                comment = TeamComment.objects.create(
                    team=team,
                    author=request.user.profile,
                    content=comment_text,
                    parent=parent_comment
                )
            else:
                comment = TeamComment.objects.create(
                    team=team,
                    author=request.user.profile,
                    content=comment_text
                )
            messages.success(request, "Comment successfully posted.")
        except TeamComment.DoesNotExist:
            messages.error(request, 'Parent comment not found.')
        return redirect('team', team_id=team.id)

    # If it's not a POST request or no message provided, render competition page
    return redirect('team', team_id=team.id)


@login_required(login_url='loginform')
def toggle_team_like(request, team_id=None, comment_id=None):
    user = request.user.profile
    if request.method == 'POST':
        item = None
        model_type = None

        if team_id:
            item = get_object_or_404(Team, id=team_id)
            model_type = 'team'
        elif comment_id:
            item = get_object_or_404(TeamComment, id=comment_id)
            model_type = 'comment'

        if not item:
            return JsonResponse({'success': False, 'error': 'Invalid like toggle request'}, status=400)

        filter_kwargs = {'user': user}
        filter_kwargs[model_type] = item
        liked = TeamLike.objects.filter(**filter_kwargs).exists()

        if liked:
            TeamLike.objects.filter(**filter_kwargs).delete()
            liked = False
        else:
            TeamLike.objects.create(**filter_kwargs)
            liked = True

        # num_likes = item.competition_likes.count()

        # Count the likes using the correct related_name
        if model_type == 'team':
            num_likes = item.team_likes.count()
        elif model_type == 'comment':
            num_likes = item.team_likes.count()

        return JsonResponse({'success': True, 'liked': liked, 'num_likes': num_likes})
    else:
        return JsonResponse({'success': False, 'error': 'This request requires POST method.'}, status=400)




@login_required(login_url='loginform')
def delete_team_comment(request, comment_id):
    comment = get_object_or_404(TeamComment, id=comment_id)
    
    if request.user.profile == comment.author:
        comment.delete()
        messages.success(request, "Comment successfully deleted.")
    else:
        messages.error(request, "You do not have permission to delete this comment.")
    
    return redirect('competition', team_id=comment.team.id)






def aggregate_team_statistics(match):
    # Aggregate match statistics for home and away teams
    stats_home = MatchStatistic.objects.filter(match=match, team=match.home_team).aggregate(
        shots_on_goal_home=Sum('shots_on_goal'),
        total_shots_home=Sum('total_shots'),
        fouls_home=Sum('fouls'),
        corners_home=Sum('corners'),
        offsides_home=Sum('offsides'),
        possession_percentage_home=Sum('possession_percentage'),
    )

    stats_away = MatchStatistic.objects.filter(match=match, team=match.away_team).aggregate(
        shots_on_goal_away=Sum('shots_on_goal'),
        total_shots_away=Sum('total_shots'),
        fouls_away=Sum('fouls'),
        corners_away=Sum('corners'),
        offsides_away=Sum('offsides'),
        possession_percentage_away=Sum('possession_percentage'),
    )

    # Count yellow and red cards for home and away teams
    yellow_cards_home = Card.objects.filter(
        match=match,
        player__registrations__team=match.home_team,
        player__registrations__competition=match.competition,  # Ensuring the registration is for this competition
        card_type=Card.YELLOW
    ).count()

    red_cards_home = Card.objects.filter(
        match=match,
        player__registrations__team=match.home_team,
        player__registrations__competition=match.competition,  # Ensuring the registration is for this competition
        card_type=Card.RED
    ).count()

    yellow_cards_away = Card.objects.filter(
        match=match,
        player__registrations__team=match.away_team,
        player__registrations__competition=match.competition,  # Ensuring the registration is for this competition
        card_type=Card.YELLOW
    ).count()

    red_cards_away = Card.objects.filter(
        match=match,
        player__registrations__team=match.away_team,
        player__registrations__competition=match.competition,  # Ensuring the registration is for this competition
        card_type=Card.RED
    ).count()

    # Incorporate card stats into the stats dictionaries
    stats_home.update({
        'yellow_cards_home': yellow_cards_home,
        'red_cards_home': red_cards_home,
    })

    stats_away.update({
        'yellow_cards_away': yellow_cards_away,
        'red_cards_away': red_cards_away,
    })

    return stats_home, stats_away




