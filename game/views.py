from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db import models
from .models import Game, Player, Board, Turn, Action, Tile
import json
import random


def game_lobby(request):
    """Display all available games and allow creating new ones."""
    games = Game.objects.filter(status__in=['waiting', 'active']).order_by('-created_at')
    boards = Board.objects.filter(is_active=True)
    
    context = {
        'games': games,
        'boards': boards,
    }
    return render(request, 'game/lobby.html', context)


@login_required
@require_http_methods(["POST"])
def create_game(request):
    """Create a new game."""
    board_id = request.POST.get('board_id')
    game_name = request.POST.get('game_name', 'New Game')
    game_mode = request.POST.get('game_mode', 'friends')
    max_players = int(request.POST.get('max_players', 4))
    
    board = get_object_or_404(Board, id=board_id, is_active=True)
    
    game = Game.objects.create(
        board=board,
        owner=request.user,
        name=game_name,
        mode=game_mode,
        max_players=max_players,
        status='waiting'
    )
    
    # Create player for the creator
    Player.objects.create(
        game=game,
        user=request.user,
        name=request.user.username,
        money=game.starting_money,
        turn_order=0,
        is_active=True,
        is_ready=False
    )
    
    return redirect('game:game_detail', game_id=game.id)


@login_required
@require_http_methods(["POST"])
def join_game(request, game_id):
    """Join an existing game."""
    game = get_object_or_404(Game, id=game_id, status='waiting')
    
    # Check if game is full
    if game.is_full():
        return JsonResponse({'error': 'Game is full'}, status=400)
    
    # Check if player is already in the game
    existing_player = game.players.filter(user=request.user).first()
    if existing_player:
        return redirect('game:game_detail', game_id=game.id)
    
    # Use transaction to ensure atomicity and prevent race conditions
    with transaction.atomic():
        # Get all active players and find the next available turn order
        existing_turn_orders = set(
            game.players.filter(is_active=True).values_list('turn_order', flat=True)
        )
        
        # Find the smallest available turn_order
        next_turn_order = 0
        while next_turn_order in existing_turn_orders:
            next_turn_order += 1
        
        # Create player
        Player.objects.create(
            game=game,
            user=request.user,
            name=request.user.username,
            money=game.starting_money,
            turn_order=next_turn_order,
            is_active=True,
            is_ready=False
        )
    
    return redirect('game:game_detail', game_id=game.id)


def game_detail(request, game_id):
    """Display the game board and state."""
    game = get_object_or_404(Game, id=game_id)
    players = game.players.filter(is_active=True).order_by('turn_order')
    
    # Get or create player for current user if authenticated
    current_player = None
    if request.user.is_authenticated:
        current_player = players.filter(user=request.user).first()
    
    # Get current turn
    current_turn = game.turns.filter(is_complete=False).order_by('-turn_number').first()
    
    # Get tiles for the board
    tiles = game.board.tiles.all().order_by('position')
    
    # Check if board has tiles
    if tiles.count() == 0:
        # Show message if board has no tiles
        from django.contrib import messages
        messages.warning(request, 
            f'This board ({game.board.name}) has no tiles yet. '
            'Please populate the board with tiles using the admin panel or management command.'
        )
    
    context = {
        'game': game,
        'players': players,
        'current_player': current_player,
        'current_turn': current_turn,
        'tiles': tiles,
        'tile_count': tiles.count(),
    }
    return render(request, 'game/game_detail.html', context)


@login_required
@require_http_methods(["POST"])
def start_game(request, game_id):
    """Start a game."""
    game = get_object_or_404(Game, id=game_id)
    
    # Check if user is the game owner
    if game.owner != request.user:
        return JsonResponse({'error': 'Only the game owner can start the game'}, status=403)
    
    # Check if all players are ready
    if not game.all_players_ready():
        not_ready = [p.name for p in game.players.filter(is_active=True, is_ready=False)]
        return JsonResponse({
            'error': f'Not all players are ready. Waiting for: {", ".join(not_ready)}'
        }, status=400)
    
    # Check if game can start
    if not game.can_start():
        return JsonResponse({'error': 'Game cannot start yet (need at least 2 players)'}, status=400)
    
    # Start the game
    game.status = 'active'
    game.save()
    
    # Create first turn for first player
    first_player = game.players.order_by('turn_order').first()
    Turn.objects.create(
        game=game,
        player=first_player,
        turn_number=1,
        round_number=1,
        phase='roll'
    )
    
    return JsonResponse({'success': True, 'message': 'Game started!'})


@login_required
@require_http_methods(["POST"])
def toggle_ready(request, game_id):
    """Toggle player's ready state."""
    game = get_object_or_404(Game, id=game_id, status='waiting')
    
    # Get player
    player = game.players.filter(user=request.user, is_active=True).first()
    if not player:
        return JsonResponse({'error': 'You are not in this game'}, status=403)
    
    # Toggle ready state
    is_ready = player.toggle_ready()
    
    # Check if all players are ready
    all_ready = game.all_players_ready()
    
    return JsonResponse({
        'success': True,
        'is_ready': is_ready,
        'all_ready': all_ready,
        'message': f'You are {"ready" if is_ready else "not ready"}'
    })


@login_required
@require_http_methods(["POST"])
def roll_dice(request, game_id):
    """Roll dice for current player's turn."""
    game = get_object_or_404(Game, id=game_id, status='active')
    
    # Get current player
    player = game.players.filter(user=request.user, is_active=True).first()
    if not player:
        return JsonResponse({'error': 'You are not in this game'}, status=403)
    
    # Get current turn
    current_turn = game.turns.filter(is_complete=False, player=player).order_by('-turn_number').first()
    if not current_turn:
        return JsonResponse({'error': 'Not your turn'}, status=400)
    
    if current_turn.phase != 'roll':
        return JsonResponse({'error': 'Cannot roll dice in this phase'}, status=400)
    
    # Roll two dice
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    total = dice1 + dice2
    
    # Update turn with dice roll
    current_turn.dice_roll = {'dice1': dice1, 'dice2': dice2, 'total': total}
    current_turn.phase = 'move'
    current_turn.save()
    
    # Record action
    Action.objects.create(
        turn=current_turn,
        player=player,
        action_type='roll_dice',
        data={'dice': [dice1, dice2], 'total': total},
        is_successful=True
    )
    
    # Move player
    old_position = player.position
    new_position = (old_position + total) % 40  # Assuming 40 spaces
    
    # Check if passed GO
    passed_go = new_position < old_position
    if passed_go:
        player.money += 200
    
    player.position = new_position
    player.save()
    
    # Update turn phase
    current_turn.phase = 'action'
    current_turn.save()
    
    # Record movement action
    Action.objects.create(
        turn=current_turn,
        player=player,
        action_type='move',
        data={'from': old_position, 'to': new_position, 'passed_go': passed_go},
        is_successful=True
    )
    
    return JsonResponse({
        'success': True,
        'dice1': dice1,
        'dice2': dice2,
        'total': total,
        'new_position': new_position,
        'passed_go': passed_go,
        'money': player.money
    })


@login_required
@require_http_methods(["POST"])
def buy_property(request, game_id):
    """Buy property at current position."""
    game = get_object_or_404(Game, id=game_id, status='active')
    
    # Get current player
    player = game.players.filter(user=request.user, is_active=True).first()
    if not player:
        return JsonResponse({'error': 'You are not in this game'}, status=403)
    
    # Get current turn
    current_turn = game.turns.filter(is_complete=False, player=player).order_by('-turn_number').first()
    if not current_turn:
        return JsonResponse({'error': 'Not your turn'}, status=400)
    
    # Get tile at current position
    try:
        tile = game.board.tiles.get(position=player.position)
    except Tile.DoesNotExist:
        return JsonResponse({'error': 'No tile at this position'}, status=400)
    
    # Check if tile can be bought
    if tile.terrain_type not in ['property', 'railroad', 'utility']:
        return JsonResponse({'error': 'This tile cannot be purchased'}, status=400)
    
    if tile.owner is not None:
        return JsonResponse({'error': 'This property is already owned'}, status=400)
    
    if player.money < tile.price:
        return JsonResponse({'error': 'Insufficient funds'}, status=400)
    
    # Buy the property
    with transaction.atomic():
        player.money -= tile.price
        player.save()
        
        tile.owner = player
        tile.save()
        
        # Record action
        Action.objects.create(
            turn=current_turn,
            player=player,
            action_type='buy',
            target_tile=tile,
            amount=tile.price,
            data={'tile_name': tile.name, 'price': tile.price},
            is_successful=True
        )
    
    return JsonResponse({
        'success': True,
        'tile_name': tile.name,
        'price': tile.price,
        'remaining_money': player.money
    })


@login_required
@require_http_methods(["POST"])
def end_turn(request, game_id):
    """End current player's turn."""
    game = get_object_or_404(Game, id=game_id, status='active')
    
    # Get current player
    player = game.players.filter(user=request.user, is_active=True).first()
    if not player:
        return JsonResponse({'error': 'You are not in this game'}, status=403)
    
    # Get current turn
    current_turn = game.turns.filter(is_complete=False, player=player).order_by('-turn_number').first()
    if not current_turn:
        return JsonResponse({'error': 'Not your turn'}, status=400)
    
    # Complete the turn
    current_turn.complete()
    
    # Get next player
    all_players = list(game.players.filter(is_active=True).order_by('turn_order'))
    current_index = next(i for i, p in enumerate(all_players) if p.id == player.id)
    next_index = (current_index + 1) % len(all_players)
    next_player = all_players[next_index]
    
    # Determine next turn and round numbers
    next_turn_number = current_turn.turn_number + 1
    next_round_number = current_turn.round_number
    
    # If we're back to the first player, increment round
    if next_index == 0:
        next_round_number += 1
    
    # Create next turn
    Turn.objects.create(
        game=game,
        player=next_player,
        turn_number=next_turn_number,
        round_number=next_round_number,
        phase='roll'
    )
    
    return JsonResponse({
        'success': True,
        'next_player_name': next_player.name,
        'next_turn_number': next_turn_number,
        'next_round_number': next_round_number
    })


def game_state(request, game_id):
    """Get current game state as JSON."""
    game = get_object_or_404(Game, id=game_id)
    
    # Get players
    players_data = []
    for player in game.players.filter(is_active=True).order_by('turn_order'):
        players_data.append({
            'id': player.id,
            'name': player.name,
            'money': player.money,
            'position': player.position,
            'turn_order': player.turn_order,
            'level': player.level,
            'experience': player.experience,
            'score': player.score,
        })
    
    # Get current turn
    current_turn = game.turns.filter(is_complete=False).order_by('-turn_number').first()
    current_turn_data = None
    if current_turn:
        current_turn_data = {
            'turn_number': current_turn.turn_number,
            'round_number': current_turn.round_number,
            'phase': current_turn.phase,
            'player_id': current_turn.player.id,
            'player_name': current_turn.player.name,
            'dice_roll': current_turn.dice_roll,
        }
    
    # Get tiles with ownership
    tiles_data = []
    for tile in game.board.tiles.all().order_by('position'):
        tiles_data.append({
            'id': tile.id,
            'position': tile.position,
            'name': tile.name,
            'terrain_type': tile.terrain_type,
            'price': tile.price,
            'rent': tile.rent,
            'owner_id': tile.owner.id if tile.owner else None,
            'owner_name': tile.owner.name if tile.owner else None,
            'improvement_level': tile.improvement_level,
        })
    
    return JsonResponse({
        'game': {
            'id': game.id,
            'name': game.name,
            'status': game.status,
            'mode': game.mode,
            'max_players': game.max_players,
            'current_players': game.get_active_players_count(),
        },
        'players': players_data,
        'current_turn': current_turn_data,
        'tiles': tiles_data,
    })
