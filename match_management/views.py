from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as authlogin, logout as authlogout
from django.contrib.auth.decorators import login_required
from collections import defaultdict


from django.http import JsonResponse
from django.contrib import messages





from .models import Match, MatchComment, MatchLike, Goal, PenaltyShootout, Card, Substitution, Foul, Save, Injury
from match_management.models import PlayerRegistration
from user_management.models import UserProfile
from competition_management.views import aggregate_team_statistics


def matchresultdetails(request, match_id):
    match = get_object_or_404(Match.objects.prefetch_related(
        'competition', 
        'home_team', 
        'away_team',
        'details',  # Assuming details refers to the related Result
        'match_comments__match_replies__match_likes',
        'match_comments__match_likes', 
        'match_likes'
    ), pk=match_id)

    result = match.details  # Ensure you have checks for None below where necessary
    competition = match.competition

    home_team_players = PlayerRegistration.objects.filter(
        team=match.home_team, competition=competition
    ).select_related('player', 'team').order_by('player__position')

    away_team_players = PlayerRegistration.objects.filter(
        team=match.away_team, competition=competition
    ).select_related('player', 'team').order_by('player__position')

    stats_home, stats_away = aggregate_team_statistics(match)

    cards_home = Card.objects.filter(match=match, player__registrations__team=match.home_team, player__registrations__competition=competition)
    cards_away = Card.objects.filter(match=match, player__registrations__team=match.away_team, player__registrations__competition=competition)

    # Card counts
    yellow_cards_home = cards_home.filter(card_type=Card.YELLOW).count()
    red_cards_home = cards_home.filter(card_type=Card.RED).count()
    yellow_cards_away = cards_away.filter(card_type=Card.YELLOW).count()
    red_cards_away = cards_away.filter(card_type=Card.RED).count()

    # Save counts
    saves_home_count = Save.objects.filter(match=match, goalkeeper__registrations__team=match.home_team, goalkeeper__registrations__competition=competition).count()
    saves_away_count = Save.objects.filter(match=match, goalkeeper__registrations__team=match.away_team, goalkeeper__registrations__competition=competition).count()

    # Goals, substitutions, saves, penalties
    goals = Goal.objects.filter(match=match).select_related('scorer', 'assist')
    substitutions = Substitution.objects.filter(match=match).select_related('player_out', 'player_in')
    saves = Save.objects.filter(match=match).select_related('goalkeeper')

    home_team_penalty_score = PenaltyShootout.objects.filter(result=result, is_shootout=True, team=match.home_team, is_scored=True).count() if result else 0
    away_team_penalty_score = PenaltyShootout.objects.filter(result=result, is_shootout=True, team=match.away_team, is_scored=True).count() if result else 0

    regular_penalties = PenaltyShootout.objects.filter(result=result, is_shootout=False) if result else []
    shootout_penalties_home = PenaltyShootout.objects.filter(result=result, is_shootout=True, team=match.home_team) if result else []
    shootout_penalties_away = PenaltyShootout.objects.filter(result=result, is_shootout=True, team=match.away_team) if result else []


    # Fetch game events by minute
    game_events_by_minute = aggregate_game_events_by_minute(goals, cards_home | cards_away, substitutions, saves, regular_penalties)

    # Split the game events into first half and second half events
    first_half_events = {}
    second_half_events = {}
    halftime_marker_needed = False  # This variable tracks whether we need to display 'HT'

    for minute, events in game_events_by_minute.items():
        if minute <= 45:  # First half events
            first_half_events[minute] = events
        else:  # Second half events
            second_half_events[minute] = events
            halftime_marker_needed = True  # If there's a second-half event, HT should be displayed


    
    login_user_profile = None
    comments = None
    num_comments = 0
    num_likes = 0

    if request.user.is_authenticated:
        login_user_profile = UserProfile.objects.get(user=request.user)
        comments = match.match_comments.filter(parent__isnull=True)
        num_comments = comments.count()
        num_likes = match.match_likes.count()
        match.user_has_liked = match.match_likes.filter(user=login_user_profile).exists()

        for comment in match.match_comments.all():
            comment.num_likes = comment.match_likes.count()
            comment.user_has_liked = comment.match_likes.filter(user=login_user_profile).exists()
            comment.num_replies = comment.match_replies.count()

            for reply in comment.match_replies.all():
                reply.num_likes = reply.match_likes.count()
                reply.user_has_liked = reply.match_likes.filter(user=login_user_profile).exists()

    context = {
        'match': match,
        'result': result,
        'competition': competition,
        'stats_home': stats_home,
        'stats_away': stats_away,
        'yellow_cards_home': yellow_cards_home,
        'red_cards_home': red_cards_home,
        'yellow_cards_away': yellow_cards_away,
        'red_cards_away': red_cards_away,
        'saves_home_count': saves_home_count,
        'saves_away_count': saves_away_count,
        'game_events_by_minute': game_events_by_minute,
        'first_half_events': first_half_events,  # Pass first half events
        'second_half_events': second_half_events,  # Pass second half events
        'halftime_marker_needed': halftime_marker_needed,  # Indicate if HT should be shown
        'added_time': result.added_time if result else None,
        'man_of_the_match': result.man_of_the_match if result else None,
        'regular_penalties': regular_penalties,
        'shootout_penalties_home': shootout_penalties_home,
        'shootout_penalties_away': shootout_penalties_away,
        'home_team_penalty_score': home_team_penalty_score,
        'away_team_penalty_score': away_team_penalty_score,
        'over_time': result.added_time if result else None,
        'home_team_players': home_team_players,
        'away_team_players': away_team_players,
        'login_user': login_user_profile,
        'comments': comments,
        'num_comments': num_comments,
        'num_likes': num_likes
    }

    return render(request, 'matchresultdetails.html', context)


def aggregate_game_events_by_minute(goals, cards, substitutions, saves, regular_penalties):
    game_events_by_minute = defaultdict(lambda: {'home_events': [], 'away_events': []})

    def full_name(player):
        return player.name.get_full_name()

    # Goals
    for goal in goals:
        if goal.is_own_goal:
            goal_detail = "Own goal"  # Set the detail for own goals
            is_own_goal = True
            team = 'home' if goal.scorer.registrations.filter(team=goal.match.away_team).exists() else 'away'
        else:
            goal_detail = f"{full_name(goal.scorer)}"  # Regular goal detail
            is_own_goal = False
            team = 'home' if goal.scorer.registrations.filter(team=goal.match.home_team).exists() else 'away'

        event_info = {
            'event': "Goal",
            'player_id': goal.scorer.id,
            'detail': goal_detail,
            'player_name': full_name(goal.scorer),  # Always the goal scorer's name
            'assist_name': full_name(goal.assist) if goal.assist else None,
            'is_own_goal': is_own_goal,
            'team': team
        }

        game_events_by_minute[goal.minute]['home_events' if team == 'home' else 'away_events'].append(event_info)

    # Regular Penalties
    for penalty in regular_penalties:
        penalty_detail = f"Penalty {'missed' if penalty.is_missed else 'scored'}"
        event_info = {
            'event': "Penalty",
            'player_id': penalty.player.id,
            'detail': penalty_detail,
            'player_name': full_name(penalty.player),
            'is_missed': penalty.is_missed,
            'team': 'home' if penalty.player.registrations.filter(team=penalty.result.match.home_team).exists() else 'away'
        }

        game_events_by_minute[penalty.minute]['home_events' if event_info['team'] == 'home' else 'away_events'].append(event_info)
    
    # Cards
    for card in cards:
        # Skip yellow cards that were upgraded to a red card due to a second yellow
        if card.card_type == Card.YELLOW and card.is_second_yellow:
            continue

        event_type = 'Second Yellow Card' if card.is_second_yellow else ('Yellow Card' if card.card_type == Card.YELLOW else 'Red Card')
        event_info = {
            'event': event_type,
            'player_id': card.player.id,
            'detail': 'Second yellow card' if card.is_second_yellow else ('Yellow card' if card.card_type == Card.YELLOW else 'Red card'),
            'player_name': full_name(card.player),
            'is_second_yellow': card.is_second_yellow,
            'team': 'home' if card.player.registrations.filter(team=card.match.home_team).exists() else 'away'
        }

        game_events_by_minute[card.minute]['home_events' if event_info['team'] == 'home' else 'away_events'].append(event_info)

    # Substitutions
    for sub in substitutions:
        event_info = {
            'event': "Substitution",
            'player_out': full_name(sub.player_out),
            'player_in': full_name(sub.player_in),
            'team': 'home' if sub.player_out.registrations.filter(team=sub.match.home_team).exists() else 'away'
        }

        game_events_by_minute[sub.minute]['home_events' if event_info['team'] == 'home' else 'away_events'].append(event_info)

    # Saves
    for save in saves:
        event_info = {
            'event': "Save",
            'goalkeeper_id': save.goalkeeper.id,
            'player_name': full_name(save.goalkeeper),
            'team': 'home' if save.goalkeeper.registrations.filter(team=save.match.home_team).exists() else 'away'
        }

        game_events_by_minute[save.minute]['home_events' if event_info['team'] == 'home' else 'away_events'].append(event_info)

    return dict(sorted(game_events_by_minute.items()))


@login_required(login_url='loginform')
def match_comment(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if request.method == "POST" and request.POST.get('message'):
        comment_text = request.POST.get('message')
        parent_id = request.POST.get('parent_id', None)
        try:
            if parent_id:
                parent_comment = MatchComment.objects.get(id=parent_id)
                comment = MatchComment.objects.create(
                    match=match,
                    author=request.user.profile,
                    content=comment_text,
                    parent=parent_comment
                )
            else:
                comment = MatchComment.objects.create(
                    match=match,
                    author=request.user.profile,
                    content=comment_text
                )
            messages.success(request, "Comment successfully posted.")
        except MatchComment.DoesNotExist:
            messages.error(request, 'Parent comment not found.')
        return redirect('matchresultdetails', match_id=match.id)

    return redirect('matchresultdetails', match_id=match.id)


@login_required(login_url='loginform')
def toggle_match_like(request, match_id=None, comment_id=None):
    user = request.user.profile
    if request.method == 'POST':
        item = None
        model_type = None

        if match_id:
            item = get_object_or_404(Match, id=match_id)
            model_type = 'match'
        elif comment_id:
            item = get_object_or_404(MatchComment, id=comment_id)
            model_type = 'comment'

        if not item:
            return JsonResponse({'success': False, 'error': 'Invalid like toggle request'}, status=400)

        filter_kwargs = {'user': user}
        filter_kwargs[model_type] = item
        liked = MatchLike.objects.filter(**filter_kwargs).exists()

        if liked:
            MatchLike.objects.filter(**filter_kwargs).delete()
            liked = False
        else:
            MatchLike.objects.create(**filter_kwargs)
            liked = True

        # Count the likes using the correct related_name
        if model_type == 'match':
            num_likes = item.match_likes.count()
        elif model_type == 'comment':
            num_likes = item.match_likes.count()

        return JsonResponse({'success': True, 'liked': liked, 'num_likes': num_likes})
    else:
        return JsonResponse({'success': False, 'error': 'This request requires POST method.'}, status=400)


@login_required(login_url='loginform')
def delete_match_comment(request, comment_id):
    comment = get_object_or_404(MatchComment, id=comment_id)
    
    if request.user.profile == comment.author:
        comment.delete()
        messages.success(request, "Comment successfully deleted.")
    else:
        messages.error(request, "You do not have permission to delete this comment.")
    
    return redirect('matchresultdetails', match_id=comment.match.id)


