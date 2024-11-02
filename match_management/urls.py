from django.urls import path
from . import views


urlpatterns = [
    
    path('matchresultdetails/<int:match_id>/details/', views.matchresultdetails, name='matchresultdetails'),

    path('match/<int:match_id>/comment/', views.match_comment, name='match_comment'),
    path('match/comment/<int:comment_id>/delete/', views.delete_match_comment, name='delete_match_comment'),
    path('toggle_match_like/<int:match_id>/', views.toggle_match_like, name='toggle_competition_like'),
    path('toggle_match_like/comment/<int:comment_id>/', views.toggle_match_like, name='toggle_match_like_comment'),
    path('toggle_match_like/comment/<int:child_comment_id>/', views.toggle_match_like, name='toggle_match_like_child_comment'),
]