from django.urls import path

from . import views


urlpatterns = [

    
    path('competition/<int:competition_id>/', views.competition, name='competition'),
    path('competition/<int:competition_id>/info', views.competition_info, name='competition_info'),
    
    
    
    path('competition/<int:competition_id>/comment/', views.competition_comment, name='competition_comment'),
    path('competition/comment/<int:comment_id>/delete/', views.delete_competition_comment, name='delete_competition_comment'),
    path('toggle_competition_like/<int:competition_id>/', views.toggle_competition_like, name='toggle_competition_like'),
    path('toggle_competition_like/comment/<int:comment_id>/', views.toggle_competition_like, name='toggle_competition_like_comment'),
    path('toggle_competition_like/comment/<int:child_comment_id>/', views.toggle_competition_like, name='toggle_competition_like_child_comment'),

    path('competition/<int:competition_id>//load_more_fixtures/', views.load_more_fixtures, name='load_more_fixtures'),

    

    path('player/<int:player_id>/', views.player, name='player'),

    path('player/<int:player_id>/change_picture/', views.change_player_picture, name='change_player_picture'),
    path('player/edit/<int:player_id>/', views.edit_player_info, name='edit_player_info'),

    path('upload_player_post/<int:player_id>/', views.upload_player_post, name='upload_player_post'),
    path('load_more_posts/<int:player_id>/', views.load_more_posts, name='load_more_posts'),

    path('player/<int:player_id>/comment/', views.player_comment, name='player_comment'),
    path('player/comment/<int:comment_id>/delete/', views.delete_player_comment, name='delete_player_comment'),

    path('toggle_player_like/<int:player_id>/', views.toggle_player_like, name='toggle_player_like'),
    path('toggle_player_like/comment/<int:comment_id>/', views.toggle_player_like, name='toggle_player_like_comment'),
    path('toggle_player_like/comment/<int:child_comment_id>/', views.toggle_player_like, name='toggle_player_like_child_comment'),






    path('team/<int:team_id>/', views.team, name='team'),
    # path('team/<int:team_id>/<int:competition_id>/', views.team, name='team'),
    path('team/<int:team_id>/add_player/', views.add_player_to_team, name='add_player_to_team'),
    path('team/<int:team_id>/comment/', views.team_comment, name='team_comment'),
    path('team/comment/<int:comment_id>/delete/', views.delete_team_comment, name='delete_team_comment'),

    path('toggle_team_like/<int:team_id>/', views.toggle_team_like, name='toggle_team_like'),
    path('toggle_team_like/comment/<int:comment_id>/', views.toggle_team_like, name='toggle_team_like_comment'),
    path('toggle_team_like/comment/<int:child_comment_id>/', views.toggle_team_like, name='toggle_team_like_child_comment'),

]