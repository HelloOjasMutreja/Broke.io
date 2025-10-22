from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    # Game lobby - list all games and create new ones
    path('', views.game_lobby, name='lobby'),
]
