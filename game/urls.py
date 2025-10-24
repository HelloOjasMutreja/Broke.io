from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    # Game lobby - list all games and create new ones
    path('', views.game_lobby, name='lobby'),
    # Create a new game
    path('create/', views.create_game, name='create_game'),
    # Join an existing game
    path('<int:game_id>/join/', views.join_game, name='join_game'),
    # View game detail
    path('<int:game_id>/', views.game_detail, name='game_detail'),
]
