from django.shortcuts import render
from django.http import JsonResponse

# Placeholder views during model migration
# TODO: Update views to work with new model structure

def game_lobby(request):
    """Display all available games and allow creating new ones."""
    return render(request, 'game/lobby.html', {})
