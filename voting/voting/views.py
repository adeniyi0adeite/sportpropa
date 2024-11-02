from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from decimal import Decimal
import uuid
import random
import string
import requests

from django.db.models import Sum
from django.core.mail import EmailMessage



from .models import AwardCategory, Vote
from competition_management.models import Player, Team, PlayerRegistration, Competition, Coach, TeamCoachCompetition
from user_management.utils import send_mail




# Helper function to aggregate votes
def aggregate_votes(queryset, category_field, competition=None):
    vote_queryset = queryset.filter(category=category_field)
    if competition:
        vote_queryset = vote_queryset.filter(competition=competition)
    return vote_queryset.aggregate(Sum('num_of_votes'))['num_of_votes__sum'] or 0


def vote_home(request):
    competitions = Competition.objects.all()
    latest_competition = competitions.order_by('-created_at').first()
    all_categories = AwardCategory.objects.all()

    player_categories = ['most_valuable_player', 'best_player', 'top_scorer', 'best_goalkeeper']
    team_categories = ['best_team']
    coach_categories = ['best_coach']

    player_categories_list = []
    team_categories_list = []
    coach_categories_list = []

    # Get total votes for players
    for cat in all_categories.filter(category__in=player_categories):
        nominees = cat.nominees.all()
        for nominee in nominees:
            nominee.total_votes = aggregate_votes(
                Vote.objects.filter(player=nominee),
                category_field=cat.category,
                competition=cat.competition
            )
            # Find the team the nominee belongs to (if applicable)
            nominee.team = PlayerRegistration.objects.filter(player=nominee, competition=cat.competition).first().team
            
        player_categories_list.append({
            'category': cat,
            'nominees': nominees,
            'hide_vote_count': cat.hide_vote_count,  # Add this field
        })

    # Get total votes for teams
    for cat in all_categories.filter(category__in=team_categories):
        teams = cat.teams.all()
        for team in teams:
            team.total_votes = aggregate_votes(
                Vote.objects.filter(team=team),
                category_field=cat.category
            )
        team_categories_list.append({
            'category': cat,
            'teams': teams,
            'hide_vote_count': cat.hide_vote_count,  # Add this field
        })

    # Get total votes for coaches and find the team each coach represents in the competition
    for cat in all_categories.filter(category__in=coach_categories):
        coaches = cat.coaches.all()
        coach_data_list = []
        for coach in coaches:
            coach.total_votes = aggregate_votes(
                Vote.objects.filter(coach=coach),
                category_field=cat.category
            )
            # Find the team the coach represents in the competition
            team_coach_competition = TeamCoachCompetition.objects.filter(coach=coach, competition=cat.competition).first()

            coach_data_list.append({
                'coach': coach,
                'team': team_coach_competition.team if team_coach_competition else None,  # Ensure team exists
                'total_votes': coach.total_votes,
            })

        coach_categories_list.append({
            'category': cat,
            'coaches': coach_data_list,
            'hide_vote_count': cat.hide_vote_count,  # Add this field
        })

    context = {
        'player_categories': player_categories_list,
        'team_categories': team_categories_list,
        'coach_categories': coach_categories_list,
        'competitions': competitions,
        'latest_competition': latest_competition,
    }

    return render(request, 'vote.html', context)



PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY

def initialize_payment(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        num_of_votes = request.POST.get('num_of_votes')
        nominee_id = request.POST.get('nominee_id')
        category_id = request.POST.get('category_id')

        # Log category for debugging
        print(f"Category ID received from form: {category_id}, {nominee_id}")

        # Validate email and number of votes
        if not email or not num_of_votes:
            messages.error(request, 'Email and number of votes are required.')
            return redirect('vote_home')

        # Fetch award_category safely
        try:
            award_category = AwardCategory.objects.get(id=category_id)
        except AwardCategory.DoesNotExist:
            messages.error(request, 'Invalid category.')
            return redirect('vote_home')

        # Check if email has voted in this category
        existing_vote = Vote.objects.filter(email=email, category=award_category.category)
        if existing_vote.filter(confirmed=True).exists():
            messages.error(request, 'You have already voted successfully in this category.')
            return redirect('vote_home')

        try:
            num_of_votes = int(num_of_votes)
            if num_of_votes <= 0:
                raise ValueError("Number of votes must be positive.")
        except (ValueError, TypeError):
            messages.error(request, 'Invalid number of votes.')
            return redirect('vote_home')

        if award_category.category == 'best_team':
            try:
                nominee = Team.objects.get(id=nominee_id)
            except Team.DoesNotExist:
                messages.error(request, 'Invalid team nominee.')
                return redirect('vote_home')
        elif award_category.category == 'best_coach':
            try:
                nominee = Coach.objects.get(id=nominee_id)
            except Coach.DoesNotExist:
                messages.error(request, 'Invalid coach nominee.')
                return redirect('vote_home')
        else:
            try:
                nominee = Player.objects.get(id=nominee_id)
            except Player.DoesNotExist:
                messages.error(request, 'Invalid player nominee.')
                return redirect('vote_home')

        amount = Decimal(num_of_votes) * Decimal('100.00')  # Total amount in Naira
        amount_in_kobo = int(amount * 100)  # Convert amount to kobo

        # Generate a unique reference
        transaction_reference = str(uuid.uuid4())

        # Generate a random 8-character verification code
        verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        request.session['session_verification_code'] = verification_code  # Store the verification code in the session

        # Create or update the vote entry
        vote, created = Vote.objects.update_or_create(
            email=email,
            category=award_category.category,
            defaults={
                'competition': award_category.competition,
                'team': nominee if award_category.category == 'best_team' else None,
                'player': nominee if award_category.category != 'best_team' and award_category.category != 'best_coach' else None,
                'coach': nominee if award_category.category == 'best_coach' else None,
                'num_of_votes': 0,  # Initially set to 0, updated later on successful payment
                'amount_paid': 0,  # Initially set to 0
                'transaction_reference': transaction_reference,  # Save the unique reference
                'confirmed': False  # Set as not confirmed
            }
        )

        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        data = {
            "email": email,
            "amount": amount_in_kobo,  # Amount in kobo
            "reference": transaction_reference,  # Use the unique reference
            "callback_url": request.build_absolute_uri(reverse('verify_payment')),  # Callback URL
            "metadata": {
                "num_of_votes": num_of_votes  # Include the number of votes as metadata
            }
        }

        try:
            response = requests.post('https://api.paystack.co/transaction/initialize', json=data, headers=headers)
            res_data = response.json()

            if res_data['status']:
                # Redirect to the payment authorization URL
                return redirect(res_data['data']['authorization_url'])
            else:
                messages.error(request, f"Payment initialization failed: {res_data['message']}")
                return redirect('vote_home')
        except Exception as e:
            messages.error(request, f'Something went wrong: {e}')
            return redirect('vote_home')

    return redirect('vote_home')


def verify_payment(request):
    reference = request.GET.get('reference')
    if not reference:
        return HttpResponse('No reference provided.')

    # Fetch vote using transaction_reference
    try:
        vote = Vote.objects.get(transaction_reference=reference)
    except Vote.DoesNotExist:
        return HttpResponse('Vote not found.')

    # Verify payment with Paystack
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data['status'] and res_data['data']['status'] == 'success':
        # Extract num_of_votes from metadata, with a fallback if it's missing
        num_of_votes = res_data['data']['metadata'].get('num_of_votes', 0)
        if num_of_votes == 0:
            messages.error(request, 'Number of votes could not be retrieved.')
            return redirect('vote_home')

        # Update the vote to mark the payment as successful and set the correct number of votes and amount
        vote.payment_status = True
        vote.num_of_votes = int(num_of_votes)  # Set the correct number of votes
        vote.amount_paid = Decimal(res_data['data']['amount']) / 100  # Convert amount back to Naira
        vote.confirmed = True  # Automatically mark the vote as confirmed
        vote.confirmation_id = generate_confirmation_id(vote)  # Generate confirmation ID
        vote.save()

        # Send confirmation email with confirmation ID
        send_confirmation_email(vote, vote.confirmation_id)

        # Redirect to the vote confirmed page
        return HttpResponseRedirect(reverse('vote_confirmed', args=[vote.confirmation_id]))
    else:
        messages.error(request, 'Payment verification failed. Please try again.')
        return redirect('vote_home')



def send_confirmation_email(vote, confirmation_id):
    subject = 'Vote Payment and Confirmation Details'
    message = (f'<p>Your vote has been successfully received for {vote.num_of_votes} votes.</p>'
               f'<p><strong>Payment Status:</strong> Successful</p>'
               f'<p><strong>Payment Reference:</strong> {vote.transaction_reference}</p>'
               f'<p><strong>Confirmation ID:</strong> {confirmation_id}</p>'
               f'<p>Thank you for voting in the {vote.category} category.</p>'
               f'<p>To view the status of your vote, please visit the confirmation page.</p>')
    
    email = EmailMessage(subject, message, 'info@sportpropa.com', [vote.email])
    email.content_subtype = "html"  # Set the email to HTML
    email.send(fail_silently=False)



def confirm_vote(request):
    if request.method == 'POST':
        entered_code = request.POST.get('verification_code')
        session_code = request.session.get('session_verification_code')

        if entered_code == session_code:
            try:
                email = request.session.get('email')
                vote = Vote.objects.get(email=email, confirmed=False)

                vote.confirmed = True
                vote.confirmation_id = generate_confirmation_id(vote)
                vote.save()

                # Instead of storing in session, retrieve directly from model
                confirmation_id = vote.confirmation_id

                # Redirect to the vote confirmed page
                return HttpResponseRedirect(reverse('vote_confirmed', args=[confirmation_id]))
            except Vote.DoesNotExist:
                messages.error(request, 'Invalid or expired verification code.')
        else:
            messages.error(request, 'Incorrect verification code.')

    return render(request, 'confirm_vote.html')


def resend_vote_code(request):
    # Fetch the email from the session (assuming it's stored there after initial payment)
    email = request.session.get('email')

    if not email:
        messages.error(request, 'Unable to resend the code. Please try again.')
        return redirect('confirm_vote')  # Redirect back to confirmation page if there's an error

    # Retrieve the vote object based on the email
    try:
        vote = Vote.objects.get(email=email, confirmed=False)
    except Vote.DoesNotExist:
        messages.error(request, 'Vote not found.')
        return redirect('confirm_vote')

    # Generate a new 8-character verification code
    new_verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Store the new code in the session
    request.session['session_verification_code'] = new_verification_code

    # Send the new verification code via email
    send_confirmation_email(vote, new_verification_code)

    # Notify the user
    messages.success(request, f'A new verification code has been sent to {email}.')
    
    # Redirect back to the confirmation page
    return redirect('confirm_vote')





def generate_confirmation_id(vote):
    return f"VOTE-{uuid.uuid4().hex[:8].upper()}-{vote.id}"


def vote_confirmed(request, confirmation_id):
    # Retrieve the vote using the confirmation ID
    vote = Vote.objects.filter(confirmation_id=confirmation_id).first()

    if not vote:
        messages.error(request, 'Confirmation ID is invalid.')
        return redirect('vote_home')

    # Map category codes to readable names
    category_mapping = {
        'most_valuable_player': 'MVP',
        'best_player': 'Best Player',
        'top_scorer': 'Top Scorer',
        'best_goalkeeper': 'Best Goalkeeper',
        'best_team': 'Best Team',
        'best_coach': 'Best Coach'
    }

    # Translate the category code to its readable name
    category_name = category_mapping.get(vote.category, '')

    context = {
        'confirmation_id': confirmation_id,
        'vote': vote,
        'player': vote.player if vote.player else None,
        'team': vote.team if vote.team else None,
        'coach': vote.coach if vote.coach else None,  # Add this line
        'category': category_name,
        'num_of_votes': vote.num_of_votes,
    }

    return render(request, 'vote_confirmed.html', context)



def vote_status(request, confirmation_id):
    # Retrieve the vote using the confirmation ID
    vote = get_object_or_404(Vote, confirmation_id=confirmation_id)

    # Map category codes to readable names
    category_mapping = {
        'most_valuable_player': 'MVP',
        'best_player': 'Best Player',
        'top_scorer': 'Top Scorer',
        'best_goalkeeper': 'Best Goalkeeper',
        'best_team': 'Best Team',
        'best_coach': 'Best Coach'
    }

    # Translate the category code to its readable name
    category_name = category_mapping.get(vote.category, vote.category)

    context = {
        'vote': vote,
        'category_name': category_name,
    }

    return render(request, 'vote_status.html', context)