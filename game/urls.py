from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    # Game lobby - list all games and create new ones
    path('', views.game_lobby, name='lobby'),
    
    # Create a new game
    path('create/', views.create_game, name='create_game'),
    
    # Join a game
    path('<int:game_id>/join/', views.join_game, name='join_game'),
    
    # Game play view
    path('<int:game_id>/', views.game_detail, name='game_detail'),
    
    # Game actions API
    path('<int:game_id>/roll-dice/', views.roll_dice, name='roll_dice'),
    path('<int:game_id>/buy-property/', views.buy_property, name='buy_property'),
    path('<int:game_id>/end-turn/', views.end_turn, name='end_turn'),
    path('<int:game_id>/state/', views.game_state, name='game_state'),
    
    # Start game
    path('<int:game_id>/start/', views.start_game, name='start_game'),
    
    # Toggle ready state
    path('<int:game_id>/toggle-ready/', views.toggle_ready, name='toggle_ready'),
]
