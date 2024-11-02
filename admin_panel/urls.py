from django.urls import path, include

from . import views



urlpatterns = [

    path('admin_panel/', views.admin_panel, name='admin_panel'),


    path('admin_panel/dashboard', views.dashboard, name='dashboard'),
    path('user-management/', views.user_management, name='user_management'),
    path('competition-management/', views.competition_management, name='competition_management'),
    path('team-management/', views.team_management, name='team_management'),
    path('player-management/', views.player_management, name='player_management'),
    path('manager-coach-management/', views.manager_coach_management, name='manager_coach_management'),
    
    
    
    path('match-management/', views.match_management, name='match_management'),
    path('filter-matches/', views.filter_matches, name='filter_matches'),
    path('create-match/', views.create_match, name='create_match'),
    path('update-match/<int:match_id>/', views.update_match, name='update_match'),
    path('delete-match/<int:match_id>/', views.delete_match, name='delete_match'),





    path('admin_panel/dashboard/users/', views.user_list, name='user_list'),
    path('admin_panel/dashboard/users/<int:user_id>/', views.view_user, name='view_user'),
    path('admin_panel/dashboard/users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('admin_panel/dashboard/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('admin_panel/dashboard/users/<int:user_id>/ban/', views.ban_user, name='ban_user'),
    # path('admin_panel/dashboard/users/<int:user_id>/roles/', views.manage_user_roles, name='manage_user_roles'),









    path('admin_panel/dashboard/teams/', views.team_list, name='team_list'),
    path('admin_panel/dashboard/teams/create/', views.create_team, name='create_team'),
    path('admin_panel/dashboard/teams/<int:pk>/detail/', views.team_detail, name='team_detail'),
    path('admin_panel/dashboard/teams/<int:pk>/update/', views.team_update, name='team_update'),
    path('admin_panel/dashboard/teams/delete/', views.team_delete, name='team_delete'),


    path('admin_panel/dashboard/competition/', views.competition, name='competition'),
    path('admin_panel/dashboard/competition/create/', views.competition_create, name='competition_create'),
    path('admin_panel/dashboard/competition/<int:pk>/detail/', views.competition_detail, name='competition_detail'),
    path('admin_panel/dashboard/competition/<int:pk>/update/', views.competition_update, name='competition_update'),
    path('admin_panel/dashboard/competition/delete/', views.competition_delete, name='competition_delete'),


    path('competition/<int:competition_id>/register_teams/', views.register_competition_teams, name='register_competition_teams'),
    path('competition/<int:competition_id>/create_team/', views.create_team, name='create_team'),



    path('admin_panel/dashboard/player/create/', views.player_create, name='player_create'),
    path('admin_panel/dashboard/player/<int:pk>/detail/', views.player_detail, name='player_detail'),
    path('admin_panel/dashboard/player/<int:pk>/update/', views.player_update, name='player_update'),
    path('admin_panel/dashboard/player/delete/', views.player_delete, name='player_delete'),
]