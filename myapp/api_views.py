from rest_framework import viewsets

from user_management.models import (UserProfile, Post, Comment, Like)
from competition_management.models import (Competition, Team, Player,)
from match_management.models import (Result, Match,
                     MatchStatistic, Goal, Card)
from standing_management.models import (Standing)

from .serializers import (CompetitionSerializer, TeamSerializer, PlayerSerializer, UserProfileSerializer,
                          PostSerializer, CommentSerializer, LikeSerializer, StandingSerializer, ResultSerializer,
                          MatchSerializer, MatchStatisticSerializer, GoalSerializer, CardSerializer)



class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

class StandingViewSet(viewsets.ModelViewSet):
    queryset = Standing.objects.all()
    serializer_class = StandingSerializer

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

class MatchStatisticViewSet(viewsets.ModelViewSet):
    queryset = MatchStatistic.objects.all()
    serializer_class = MatchStatisticSerializer

class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
