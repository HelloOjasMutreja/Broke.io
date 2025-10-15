# Game Models Documentation

This Django app contains comprehensive models for a strategy-based board game system inspired by Monopoly but extensible for various game types.

## Model Overview

### Core Game Management

#### Board
- **Purpose**: Represents the game world or grid layout
- **Key Fields**: name, width, height, theme, is_active
- **Relationships**: One Board → Many Games, Many Tiles
- **Methods**: `get_total_tiles()`

#### Game
- **Purpose**: Manages game sessions, states, and configurations
- **Key Fields**: board, name, mode, status, max_players, victory_condition, winner
- **Relationships**: Many Players, Many Turns, Many Trades
- **Methods**: `get_active_players_count()`, `is_full()`, `can_start()`

#### Player
- **Purpose**: Represents a participant in a game session
- **Key Fields**: user (optional for AI), game, name, token, money, position, score, level
- **Relationships**: Belongs to Game, User; Has many Cities, Resources, Actions, PowerUps
- **Methods**: `add_money()`, `remove_money()`, `add_experience()`

### Game World Elements

#### Tile
- **Purpose**: Defines grid spaces on the board
- **Key Fields**: board, position, x/y coordinates, terrain_type, owner, price, rent, improvement_level
- **Relationships**: Belongs to Board, owned by Player; Can have Cities
- **Methods**: `calculate_rent()`
- **Special**: Supports mortgaging, improvements (houses/hotels), color groups

#### City
- **Purpose**: Player-built structures on tiles
- **Key Fields**: tile, player, name, level, population, defense, production_capacity, health
- **Relationships**: Belongs to Tile and Player
- **Methods**: `upgrade()`, `repair()`

### Resources & Economy

#### Resource
- **Purpose**: Manages different resource types for players
- **Key Fields**: player, resource_type, amount, capacity, production_rate, consumption_rate
- **Resource Types**: food, gold, energy, wood, stone, iron, gems, influence
- **Methods**: `add()`, `remove()`, `has_sufficient()`, `get_net_rate()`

#### Trade
- **Purpose**: Facilitates trading between players
- **Key Fields**: game, initiator, recipient, status, initiator_offer, recipient_offer
- **Status Flow**: pending → accepted/rejected → completed

### Gameplay Mechanics

#### Turn
- **Purpose**: Manages turn-based gameplay sequence
- **Key Fields**: game, player, turn_number, round_number, phase, dice_roll, actions_taken
- **Phases**: roll → move → action → trade → build → end
- **Methods**: `complete()`

#### Action
- **Purpose**: Records all player actions during gameplay
- **Key Fields**: turn, player, action_type, target_tile, target_player, amount, data
- **Action Types**: move, buy, sell, trade, build, upgrade, attack, defend, collect, pay, roll_dice, draw_card, use_powerup, pass
- **Features**: Tracks success/failure, includes JSON data for flexibility

#### PowerUp
- **Purpose**: Special abilities and temporary bonuses
- **Key Fields**: player, powerup_type, name, duration, is_active, is_used
- **PowerUp Types**: double_rent, immunity, fast_travel, discount, steal, protection, boost, vision
- **Methods**: `activate()`, `deactivate()`

## Model Relationships Diagram

```
User (Django Auth)
  └─> Player
        ├─> Game
        │     └─> Board
        │           └─> Tile
        │                 └─> City
        ├─> Resource
        ├─> PowerUp
        ├─> Turn
        │     └─> Action
        └─> Trade (initiator/recipient)
```

## Key Features

### Database Optimization
- **Indexes**: Strategic indexes on frequently queried fields (player-game, status, timestamps)
- **Unique Constraints**: Prevents duplicate data (unique_together on player turn_order, tile position, etc.)
- **Ordering**: Default ordering for better query performance

### Data Validation
- **Validators**: MinValueValidator, MaxValueValidator on numeric fields
- **Choices**: Predefined choices for enums (game mode, terrain type, action type, etc.)
- **Constraints**: Model-level constraints for data integrity

### Extensibility
- **JSON Fields**: Flexible data storage for game-specific data (dice_roll, action_data, trade offers)
- **Resource System**: Supports multiple resource types with production/consumption
- **Action Tracking**: Comprehensive action log with target tracking

## Usage Examples

### Starting a New Game

```python
from game.models import Board, Game, Player

# Create board
board = Board.objects.create(
    name="Classic Board",
    width=11,
    height=11,
    theme="classic"
)

# Create game
game = Game.objects.create(
    board=board,
    name="Friday Night Game",
    mode="friends",
    max_players=4
)

# Add players
player1 = Player.objects.create(
    game=game,
    user=request.user,
    name="Alice",
    turn_order=0
)
```

### Processing a Turn

```python
from game.models import Turn, Action

# Create turn
turn = Turn.objects.create(
    game=game,
    player=player,
    turn_number=1,
    round_number=1,
    phase="roll"
)

# Record action
action = Action.objects.create(
    turn=turn,
    player=player,
    action_type="roll_dice",
    data={"dice": [3, 4], "total": 7}
)

# Complete turn
turn.complete()
```

### Managing Resources

```python
from game.models import Resource

# Get or create resource
resource, created = Resource.objects.get_or_create(
    player=player,
    resource_type="gold",
    defaults={"amount": 100, "capacity": 1000}
)

# Add resources
resource.add(50)

# Check availability
if resource.has_sufficient(75):
    resource.remove(75)
```

## Admin Interface

All models are registered in the Django admin with:
- Searchable fields
- Filters for common queries
- Read-only timestamp fields
- Raw ID fields for foreign keys (performance)

Access at: `/admin/game/`

## Testing

Comprehensive test suite covers:
- Model creation and validation
- Business logic methods
- Relationships between models
- Edge cases and constraints

Run tests: `python manage.py test game`

## Future Enhancements

Potential additions:
- **Card** model for chance/community chest cards
- **Achievement** model for player achievements
- **GameHistory** model for completed game analytics
- **Tournament** model for competitive play
- **Chat** model for in-game messaging
- **Notification** model for game events
