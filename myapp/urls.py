from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django.conf.urls import handler404
from . import views, api_views



handler404 = views.custom_404

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'competitions', api_views.CompetitionViewSet)
router.register(r'teams', api_views.TeamViewSet)
router.register(r'players', api_views.PlayerViewSet)
# router.register(r'userprofiles', api_views.UserProfileViewSet)
# router.register(r'posts', api_views.PostViewSet)
# router.register(r'comments', api_views.CommentViewSet)
# router.register(r'likes', api_views.LikeViewSet)
# router.register(r'standings', api_views.StandingViewSet)
# router.register(r'results', api_views.ResultViewSet)
# router.register(r'matches', api_views.MatchViewSet)
# router.register(r'matchstatistics', api_views.MatchStatisticViewSet)
# router.register(r'goals', api_views.GoalViewSet)
# router.register(r'cards', api_views.CardViewSet)


urlpatterns = [
    path('api/', include(router.urls)),

    path('error404/', views.error404, name='error404'),
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),

    path('user-posts/', views.user_posts, name='user_posts'),

    
    path('news/', views.news, name='news'),

    path('feedback/', views.feedback, name='feedback'),  # Ensure this name matches

    path('aboutus/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),

    path('search/', views.search_users, name='search_users'),
    
]