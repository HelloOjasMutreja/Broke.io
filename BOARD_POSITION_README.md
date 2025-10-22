# Board Position System

This document describes the new Board Position system implemented in the Broke.io game.

## Overview

The Board Position system provides a flexible, validated way to define game boards with automatic initialization of special tiles (START, JAIL, VACATION, GO_TO_JAIL).

## Key Concepts

### BoardPosition Model

`BoardPosition` is the central model that maps a position on a board to game content. Each position can contain either:
- A **Tile** (for special positions like START, JAIL, CHANCE, etc.)
- A **City** (for property tiles that can be owned and developed)

**Important**: Exactly one of `tile` or `city` must be set. This is enforced at the model level via validation.

### Special Positions

Every board has four special positions automatically calculated based on board size `n`:

| Position | Formula | Purpose |
|----------|---------|---------|
| START | 0 | Starting position, collect salary |
| JAIL/Prison | n - 1 | Jail or just visiting |
| VACATION | 2n - 1 | Rest stop, free parking variant |
| GO_TO_JAIL | 3n - 1 | Sends player to jail |

Example for a 10x10 board (size=10):
- START: position 0
- JAIL: position 9
- VACATION: position 19
- GO_TO_JAIL: position 29

## Usage

### Creating a Board

```python
from game.models import Board

# Create a board - special positions are auto-initialized
board = Board.objects.create(
    name="Classic Monopoly",
    size=10,
    theme="city",
    description="Standard monopoly board"
)

# Special positions are automatically created via signal
# Verify:
special_pos = board.default_special_positions()
print(special_pos)  # {'start': 0, 'prison': 9, 'vacation': 19, 'go_to_prison': 29}
```

### Manually Initializing Board Positions

```python
# You can manually call initialize_positions if needed
# This is idempotent - safe to call multiple times
board.initialize_positions()

# Check what was created
from game.models import BoardPosition
positions = BoardPosition.objects.filter(board=board)
print(f"Created {positions.count()} positions")
```

### Adding Custom Tiles

```python
from game.models import BoardPosition, Tile, TileType

# Create a custom tile
chance_tile = Tile.objects.create(
    title="Chance",
    tile_type=TileType.CHANCE,
    description="Draw a chance card",
    action={"type": "draw_card", "deck": "chance"}
)

# Place it on the board
BoardPosition.objects.create(
    board=board,
    position=7,
    tile=chance_tile
)
```

### Adding Properties (Cities)

```python
from game.models import BoardPosition, Tile, City, TileType

# Create a tile for the property
property_tile = Tile.objects.create(
    title="Park Place",
    tile_type=TileType.CUSTOM,  # Not CITY - that's been removed
    description="Luxury property"
)

# Create the city (property details)
city = City.objects.create(
    tile=property_tile,
    country="USA",
    base_price=350,
    mortgage_value=175,
    rent_base=35,
    rent_house_1=175,
    rent_house_2=500,
    rent_house_3=1100,
    rent_house_4=1300,
    rent_hotel=1500,
    house_cost=200,
    hotel_cost=200,
    color_group="Dark Blue"
)

# Place it on the board
BoardPosition.objects.create(
    board=board,
    position=37,
    city=city  # Note: city, not tile
)
```

### Querying Board Positions

```python
# Get all positions for a board
positions = BoardPosition.objects.filter(board=board).order_by('position')

# Iterate through positions
for bp in positions:
    if bp.tile:
        print(f"Position {bp.position}: {bp.tile.title} ({bp.tile.tile_type})")
    elif bp.city:
        print(f"Position {bp.position}: {bp.city.tile.title} (Property - ${bp.city.base_price})")
```

### Game Integration

```python
from game.models import Game, GameBoardTileState

# Create a game
game = Game.objects.create(
    board=board,
    owner=user,
    name="Friday Night Game"
)

# When the game starts, board state is initialized
game.initialize_board_state()

# Query per-game state
tile_states = GameBoardTileState.objects.filter(game=game)
for state in tile_states:
    if state.board_position:
        # New schema
        if state.board_position.city:
            print(f"Position {state.position}: {state.board_position.city.tile.title}")
            if state.owner:
                print(f"  Owned by: {state.owner.display_name}")
                print(f"  Houses: {state.houses}")
```

## Management Command

Use the `brokeio_seed_board` command to initialize or reset a board:

```bash
# Initialize a board (creates special positions)
python manage.py brokeio_seed_board --board-id=1

# Force re-initialization (clears all positions first)
python manage.py brokeio_seed_board --board-id=1 --force
```

Output example:
```
Processing board: Classic Monopoly (id=1)

✓ Board initialization complete!
  Total board size: 10x10 = 100 positions
  Created/existing positions: 4

  Special positions:
    Position   0 (start        ): Start
    Position   9 (prison       ): Prison/Visiting
    Position  19 (vacation     ): Vacation
    Position  29 (go_to_prison ): Go to Prison
```

## Validation

`BoardPosition` enforces strict validation:

### Valid Examples

```python
# ✅ Tile only
BoardPosition.objects.create(board=board, position=1, tile=tile)

# ✅ City only
BoardPosition.objects.create(board=board, position=2, city=city)
```

### Invalid Examples

```python
# ❌ Both tile and city set - raises ValidationError
BoardPosition.objects.create(board=board, position=3, tile=tile, city=city)

# ❌ Neither tile nor city set - raises ValidationError
BoardPosition.objects.create(board=board, position=4)
```

## Database Constraints

The `BoardPosition` model enforces:

1. **Unique Together**: `(board, position)` - each position can only be used once per board
2. **Validation**: Exactly one of `(tile, city)` must be non-null
3. **Foreign Key Constraints**: References to Board, Tile, and City are protected

## Backwards Compatibility

During migration, both `BoardTile` and `BoardPosition` models coexist:

- `BoardTile` is marked as **DEPRECATED** but still functional
- `GameBoardTileState` supports both `board_tile` (legacy) and `board_position` (new)
- `Game.initialize_board_state()` works with both schemas

See [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md) for migration instructions.

## Testing

All functionality is covered by tests in `game/tests.py`:

```bash
# Run all game tests
python manage.py test game

# Run specific test classes
python manage.py test game.tests.BoardPositionModelTest
python manage.py test game.tests.BoardInitializationTest
```

Test coverage includes:
- BoardPosition creation and validation
- Board auto-initialization
- Idempotency of initialization
- Special tile placement
- Game state initialization with new schema
- TileType enum changes

## Architecture Decisions

### Why Separate Tile and City?

Previously, `TileType.CITY` was an enum value, but properties (cities) have completely different attributes (rent, houses, price, etc.) than other tiles. By making `City` a separate model with a OneToOne relationship to `Tile`, we:

1. Keep the `Tile` model clean and focused
2. Avoid nullable fields for property-specific attributes
3. Make validation easier (either it's a property or it's not)
4. Allow properties to have a display tile while maintaining rich property data

### Why BoardPosition Instead of BoardTile?

`BoardTile` conflated the concepts of:
1. A tile definition (what it is)
2. A position on a board (where it is)

`BoardPosition` cleanly separates these concerns:
- `Tile` = what it is (definition)
- `City` = what it is (property definition)
- `BoardPosition` = where it is (placement)

This allows:
- Multiple positions to reference the same tile definition
- Clear separation between board layout and tile content
- Explicit handling of properties vs. other tiles

### Why Auto-Initialize Special Positions?

Every Monopoly-style game needs START, JAIL, etc. By auto-creating these:

1. Reduces boilerplate code when creating boards
2. Ensures consistency across all boards
3. Prevents errors (forgetting to add START, etc.)
4. Makes the system more user-friendly

The initialization is **idempotent** so it's safe to call multiple times without creating duplicates.

## Future Enhancements

Possible future improvements:

1. **Position Templates**: Pre-defined board layouts that can be applied
2. **Board Validation**: Ensure all positions 0..(n²-1) are filled before allowing game start
3. **Position Groups**: Define color groups or tile sets at the board level
4. **Dynamic Actions**: Scripted actions that can be attached to positions
5. **Board Themes**: Theme-specific tile graphics and descriptions

## API (Future)

When APIs are implemented, the board positions should be exposed as:

```json
GET /api/games/{public_id}/board

{
  "board": {
    "id": 1,
    "name": "Classic Monopoly",
    "size": 10,
    "theme": "city"
  },
  "positions": [
    {
      "position": 0,
      "type": "tile",
      "tile": {
        "title": "Start",
        "tile_type": "START",
        "description": "Collect salary when passing"
      }
    },
    {
      "position": 1,
      "type": "city",
      "city": {
        "title": "Mediterranean Avenue",
        "base_price": 60,
        "rent_base": 2,
        "color_group": "Brown"
      }
    }
  ],
  "tile_states": [
    {
      "position": 1,
      "owner": "player1",
      "houses": 2,
      "mortgaged": false
    }
  ]
}
```

## Support

For questions or issues:
1. Check the [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md)
2. Review test cases in `game/tests.py`
3. Run the management command with `--help`

## Security Summary

All code has been reviewed with CodeQL security scanner with no vulnerabilities found:
- ✅ No SQL injection risks (using Django ORM)
- ✅ No XSS vulnerabilities (no rendering of user input)
- ✅ Proper validation at model level
- ✅ Transaction safety for multi-row operations
- ✅ No exposed secrets or credentials
