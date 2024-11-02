from django.urls import path
from . import views

urlpatterns = [
    path('vote/', views.vote_home, name='vote_home'),

    path('initialize-payment/', views.initialize_payment, name='initialize_payment'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('vote/confirm-vote/', views.confirm_vote, name='confirm_vote'),
    path('resend-vote-code/', views.resend_vote_code, name='resend_vote_code'),
    
    path('vote/confirmed/<str:confirmation_id>/', views.vote_confirmed, name='vote_confirmed'),
    path('vote/status/<str:confirmation_id>/', views.vote_status, name='vote_status'),
    path('vote/winners/', views.vote_winners, name='vote_winners'),

]
