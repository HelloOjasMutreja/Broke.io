<<<<<<< HEAD
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Game, Board, Player, LobbyPlayer, GameStatus, GameMode

# Placeholder views during model migration
# TODO: Update views to work with new model structure

def game_lobby(request):
    """Display all available games and allow creating new ones."""
    # Only show ONLINE games in the public lobby
    # FRIENDS games should not be visible here (accessed via direct links)
    games = Game.objects.filter(
        mode=GameMode.ONLINE,
        status=GameStatus.LOBBY
    ).select_related('board', 'owner').order_by('-created_at')
    
    boards = Board.objects.all().order_by('name')
    
=======
5
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden
from .models import Game, Board, LobbyPlayer, Player, GameStatus
from django.contrib import messages

def game_lobby(request):
    """Display all available games and allow creating new ones."""
    games = Game.objects.select_related('board').order_by('-created_at')[:20]
    boards = Board.objects.all()
    # Add helper properties for template compatibility
    for game in games:
        game.get_active_players_count = game.lobby_players.count()
        game.is_full = game.get_active_players_count >= game.max_players
        game.get_mode_display = getattr(game, 'mode', 'Friends')
>>>>>>> fa6d470 (added board to game_detail.html)
    context = {
        'games': games,
        'boards': boards,
    }
    return render(request, 'game/lobby.html', context)

@login_required
<<<<<<< HEAD
def create_game(request):
    """Create a new game."""
    if request.method == 'POST':
        game_name = request.POST.get('game_name', 'Untitled Game')
        board_id = request.POST.get('board_id')
        game_mode = request.POST.get('game_mode', GameMode.ONLINE)
        max_players = int(request.POST.get('max_players', 4))
        
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            messages.error(request, 'Invalid board selected.')
            return redirect('game:lobby')
        
        # Create the game
        game = Game.objects.create(
            name=game_name,
            owner=request.user,
            board=board,
            mode=game_mode,
            max_players=max_players,
            status=GameStatus.LOBBY
        )
        
        # Create player for the owner
        player = Player.objects.create(
            user=request.user,
            display_name=request.user.username
        )
        
        # Add owner to lobby
        LobbyPlayer.objects.create(
            game=game,
            player=player,
            seat_index=0,
            is_owner=True
        )
        
        messages.success(request, f'Game "{game_name}" created successfully!')
        return redirect('game:game_detail', game_id=game.id)
    
    return redirect('game:lobby')

@login_required
def join_game(request, game_id):
    """Join an existing game."""
    game = get_object_or_404(Game, id=game_id)
    
    # Check if user can join
    if not game.can_user_join(request.user):
        if game.status != GameStatus.LOBBY:
            messages.error(request, 'This game has already started.')
        elif game.is_full():
            messages.error(request, 'This game is full.')
        else:
            messages.error(request, 'You cannot join this game.')
        return redirect('game:lobby')
    
    # Get or create player for this user
    player, created = Player.objects.get_or_create(
        user=request.user,
        defaults={'display_name': request.user.username}
    )
    
    # Find next available seat
    occupied_seats = set(game.lobby_players.values_list('seat_index', flat=True))
    next_seat = 0
    while next_seat in occupied_seats:
        next_seat += 1
    
    # Add player to lobby
    LobbyPlayer.objects.create(
        game=game,
        player=player,
        seat_index=next_seat,
        is_owner=False
    )
    
    messages.success(request, f'You have joined "{game.name}"!')
    return redirect('game:game_detail', game_id=game.id)

def game_detail(request, game_id):
    """Display game detail view."""
    game = get_object_or_404(Game, id=game_id)
    
    # Get current user's player if they're in the game
=======
@require_POST
def create_game(request):
    """Create a new game from the lobby form."""
    name = request.POST.get('game_name')
    board_id = request.POST.get('board_id')
    mode = request.POST.get('game_mode', 'friends')
    max_players = int(request.POST.get('max_players', 4))
    board = get_object_or_404(Board, id=board_id)
    # Create Player for user if not exists
    player, _ = Player.objects.get_or_create(user=request.user, defaults={"display_name": request.user.username})
    game = Game.objects.create(
        name=name,
        board=board,
        owner=request.user,
        max_players=max_players,
        status=GameStatus.LOBBY,
    )
    # Add creator as LobbyPlayer and owner
    LobbyPlayer.objects.create(game=game, player=player, seat_index=0, is_ready=False, is_owner=True)
    messages.success(request, f"Game '{name}' created!")
    return redirect('game:game_detail', game_id=game.id)

@login_required
@require_POST
def join_game(request, game_id):
    """Join a game from the lobby."""
    game = get_object_or_404(Game, id=game_id)
    if game.lobby_players.count() >= game.max_players:
        messages.error(request, "Game is full.")
        return redirect('game:lobby')
    player, _ = Player.objects.get_or_create(user=request.user, defaults={"display_name": request.user.username})
    if LobbyPlayer.objects.filter(game=game, player=player).exists():
        messages.info(request, "You are already in this game.")
        return redirect('game:game_detail', game_id=game.id)
    seat_index = game.lobby_players.count()
    LobbyPlayer.objects.create(game=game, player=player, seat_index=seat_index)
    messages.success(request, f"Joined game '{game.name}'!")
    return redirect('game:game_detail', game_id=game.id)

@login_required
def game_detail(request, game_id):
    """Show the detail page for a specific game."""
    game = get_object_or_404(Game, id=game_id)
    lobby_players = game.lobby_players.select_related('player').order_by('seat_index')
>>>>>>> fa6d470 (added board to game_detail.html)
    current_player = None
    if request.user.is_authenticated:
        try:
            player = Player.objects.get(user=request.user)
<<<<<<< HEAD
            current_player = game.lobby_players.filter(player=player).first()
        except Player.DoesNotExist:
            pass
    
    context = {
        'game': game,
        'players': game.lobby_players.select_related('player').all(),
=======
            current_player = lobby_players.filter(player=player).first()
        except Player.DoesNotExist:
            current_player = None
    context = {
        'game': game,
        'lobby_players': lobby_players,
>>>>>>> fa6d470 (added board to game_detail.html)
        'current_player': current_player,
    }
    return render(request, 'game/game_detail.html', context)
