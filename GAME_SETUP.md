# Game Backend Setup Guide

This guide explains how to set up and use the Django backend for the Broke.io board game.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Seed Test Data (Recommended for Testing)

Populate the database with test data including boards, tiles, games, players, cards, and more:

```bash
python manage.py seed_game_data
```

This creates:
- 3 boards (Classic, Cyber City, Fantasy Realm) with 40 tiles each
- 27 cards (Chance and Community Chest)
- 4 games in various states (waiting, active, with AI)
- 4 test user accounts (player1-4, password: testpass123)
- Sample powerups, chat messages, and game history

To clear existing data and reseed:

```bash
python manage.py seed_game_data --clear
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Access Admin Interface

```bash
python manage.py runserver
```

Visit: http://localhost:8000/admin/

### Testing the Game

After seeding data, you can:

1. **Login with test accounts**: Use player1/testpass123 (or player2-4)
2. **Join existing games**: Visit `/game/` to see available games
3. **Start a new game**: Select a board and game mode
4. **Play active games**: Join "Active Game - Mid Battle" to test mid-game features
5. **Test AI gameplay**: Join "Solo vs AI" game

The seeded data includes:
- Properties already owned by players
- Players at different positions on the board
- Active turns ready to play
- Chat messages and game history
- PowerUps and resources for testing

## Model Structure

The backend includes 10 comprehensive models:

1. **Board** - Game world/grid layout
2. **Game** - Game sessions and states
3. **Player** - Player identity and stats
4. **Tile** - Grid spaces on the board
5. **City** - Player-built structures
6. **Resource** - Resource management (gold, food, energy, etc.)
7. **Turn** - Turn-based gameplay tracking
8. **Action** - Player action logging
9. **Trade** - Player-to-player trading
10. **PowerUp** - Special abilities

## Creating Your First Game

### Via Django Shell

```bash
python manage.py shell
```

```python
from game.models import Board, Game, Player, Tile
from django.contrib.auth.models import User

# 1. Create a board
board = Board.objects.create(
    name="Main Board",
    width=11,
    height=11,
    theme="classic"
)

# 2. Create tiles for the board
for i in range(40):
    Tile.objects.create(
        board=board,
        position=i,
        x_coordinate=i % 11,
        y_coordinate=i // 11,
        name=f"Space {i}",
        terrain_type="property",
        price=100,
        rent=10
    )

# 3. Create a game
game = Game.objects.create(
    board=board,
    name="My First Game",
    mode="friends",
    max_players=4
)

# 4. Add players
user = User.objects.create_user("player1", password="pass123")
player = Player.objects.create(
    game=game,
    user=user,
    name="Player 1",
    money=1500,
    turn_order=0
)
```

### Via Admin Interface

1. Go to http://localhost:8000/admin/
2. Click "Boards" → "Add Board"
3. Fill in board details and save
4. Click "Games" → "Add Game"
5. Select the board and configure game settings
6. Click "Players" → "Add Player"
7. Associate player with game and user

## Integration with Frontend

The JavaScript frontend in `js/game.js` can be integrated with the Django backend through:

### Option 1: Django Templates (Current Approach)

The game state can be passed to templates:

```python
# views.py
from game.models import Game, Player

def game_view(request, game_id):
    game = Game.objects.get(id=game_id)
    players = game.players.filter(is_active=True)
    context = {
        'game': game,
        'players': players,
    }
    return render(request, 'game.html', context)
```

### Option 2: REST API (Future Enhancement)

Create API endpoints using Django REST Framework:

```python
# api/views.py
from rest_framework import viewsets
from game.models import Game, Player, Action
from .serializers import GameSerializer, PlayerSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
```

## Running Tests

```bash
# Run all game tests
python manage.py test game

# Run specific test class
python manage.py test game.tests.BoardModelTest

# Run with verbose output
python manage.py test game --verbosity=2
```

## Common Operations

### Check Game Status

```python
game = Game.objects.get(id=1)
print(f"Players: {game.get_active_players_count()}/{game.max_players}")
print(f"Can start: {game.can_start()}")
print(f"Is full: {game.is_full()}")
```

### Process Player Turn

```python
from game.models import Turn, Action

turn = Turn.objects.create(
    game=game,
    player=player,
    turn_number=1,
    round_number=1
)

# Record dice roll
action = Action.objects.create(
    turn=turn,
    player=player,
    action_type="roll_dice",
    data={"dice": [3, 5], "total": 8}
)

# Record movement
action = Action.objects.create(
    turn=turn,
    player=player,
    action_type="move",
    data={"from": 0, "to": 8}
)

# Complete turn
turn.complete()
```

### Manage Player Resources

```python
from game.models import Resource

# Create resource
resource = Resource.objects.create(
    player=player,
    resource_type="gold",
    amount=100,
    production_rate=10
)

# Add resources
resource.add(50)  # Now has 150

# Use resources
if resource.has_sufficient(75):
    resource.remove(75)  # Now has 75
```

### Handle Trades

```python
from game.models import Trade

trade = Trade.objects.create(
    game=game,
    initiator=player1,
    recipient=player2,
    initiator_offer={"money": 200, "tiles": [1, 2]},
    recipient_offer={"tiles": [5]},
    status="pending"
)

# Accept trade
trade.status = "accepted"
trade.save()
```

## Database Management

### Reset Database

```bash
rm db.sqlite3
python manage.py migrate
```

### View Database

```bash
python manage.py dbshell
```

### Export Data

```bash
python manage.py dumpdata game --indent=2 > game_data.json
```

### Import Data

```bash
python manage.py loaddata game_data.json
```

## Performance Tips

1. **Use select_related()** for foreign key queries:
   ```python
   players = Player.objects.select_related('game', 'user').all()
   ```

2. **Use prefetch_related()** for reverse foreign keys:
   ```python
   games = Game.objects.prefetch_related('players', 'turns').all()
   ```

3. **Use indexes** (already configured in models):
   - Player: (game, is_active)
   - Tile: (board, terrain_type)
   - Turn: (game, -turn_number)
   - Action: (player, -created_at)

4. **Bulk operations**:
   ```python
   tiles = [Tile(board=board, position=i, ...) for i in range(40)]
   Tile.objects.bulk_create(tiles)
   ```

## Troubleshooting

### Models Not Showing in Admin

Check that:
1. App is in `INSTALLED_APPS` (backend/settings.py)
2. Models are registered in `game/admin.py`
3. Server is restarted after changes

### Migration Issues

```bash
# Show migrations
python manage.py showmigrations

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset app migrations (careful!)
python manage.py migrate game zero
```

### Import Errors

Make sure Django settings are configured:
```python
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Now you can import models
from game.models import Game
```

## Next Steps

1. **Create API endpoints** - Add Django REST Framework for frontend communication
2. **Add WebSocket support** - Use Django Channels for real-time gameplay
3. **Implement game logic** - Add views and business logic for game rules
4. **Add authentication** - Integrate with user authentication system
5. **Create frontend integration** - Connect JavaScript game to Django backend

## Documentation

- Model details: See `game/README.md`
- Django docs: https://docs.djangoproject.com/
- Model field reference: https://docs.djangoproject.com/en/stable/ref/models/fields/
