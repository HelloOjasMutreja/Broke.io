# Migration Guide: BoardTile → BoardPosition

This guide explains how to migrate from the legacy `BoardTile` schema to the new `BoardPosition` schema.

## Overview

The refactor introduces several key changes:

1. **BoardPosition Model**: Replaces `BoardTile` as the primary board-placement model
2. **TileType.CITY Removed**: Properties are now exclusively modeled via the `City` model
3. **Position Removed from Tile**: Position belongs only to the board-placement layer (`BoardPosition`)
4. **Automatic Board Initialization**: Special positions are auto-populated when boards are created
5. **Game as Session Model**: Multiple `Game` instances can reference the same `Board` definition

## Schema Changes

### Before (Legacy)
```python
# BoardTile with position on Tile
class Tile(models.Model):
    title = models.CharField(max_length=120)
    tile_type = models.CharField(choices=TileType.choices)  # Includes CITY
    # ... other fields

class BoardTile(models.Model):
    board = models.ForeignKey(Board)
    tile = models.ForeignKey(Tile)
    position = models.PositiveIntegerField()
```

### After (New)
```python
# BoardPosition with validation for tile XOR city
class Tile(models.Model):
    title = models.CharField(max_length=120)
    tile_type = models.CharField(choices=TileType.choices)  # NO CITY type
    # No position field

class BoardPosition(models.Model):
    board = models.ForeignKey(Board)
    position = models.PositiveIntegerField()
    tile = models.ForeignKey(Tile, null=True, blank=True)
    city = models.ForeignKey(City, null=True, blank=True)
    # Validation: exactly one of (tile, city) must be set
```

## Migration Steps

### Step 1: Apply Database Migrations

The migration `0002_add_board_position_model.py` has been auto-generated and adds:
- New `BoardPosition` model with `unique_together` on `(board, position)`
- `board_position` field to `GameBoardTileState` (nullable for backwards compatibility)
- Marks `board_tile` field as deprecated
- Removes `CITY` from `TileType` choices

```bash
python manage.py migrate game
```

### Step 2: Migrate Existing Data

Create a data migration to convert `BoardTile` entries to `BoardPosition`:

```python
# Create with: python manage.py makemigrations game --empty --name migrate_boardtile_to_boardposition

from django.db import migrations

def migrate_board_tiles_to_positions(apps, schema_editor):
    """
    Migrate existing BoardTile instances to BoardPosition.
    For tiles with type CITY, we need to find the related City instance.
    """
    BoardTile = apps.get_model('game', 'BoardTile')
    BoardPosition = apps.get_model('game', 'BoardPosition')
    City = apps.get_model('game', 'City')
    
    for bt in BoardTile.objects.all():
        # Check if this tile is a city (has a City instance)
        try:
            city = City.objects.get(tile=bt.tile)
            # This is a property tile
            BoardPosition.objects.create(
                board=bt.board,
                position=bt.position,
                city=city,
                override_action=bt.override_action
            )
        except City.DoesNotExist:
            # This is a regular tile
            BoardPosition.objects.create(
                board=bt.board,
                position=bt.position,
                tile=bt.tile,
                override_action=bt.override_action
            )

def reverse_migration(apps, schema_editor):
    """Reverse migration: BoardPosition → BoardTile"""
    BoardPosition = apps.get_model('game', 'BoardPosition')
    BoardTile = apps.get_model('game', 'BoardTile')
    
    for bp in BoardPosition.objects.all():
        tile = bp.tile if bp.tile else bp.city.tile
        BoardTile.objects.create(
            board=bp.board,
            position=bp.position,
            tile=tile,
            override_action=bp.override_action
        )

class Migration(migrations.Migration):
    dependencies = [
        ('game', '0002_add_board_position_model'),
    ]

    operations = [
        migrations.RunPython(
            migrate_board_tiles_to_positions,
            reverse_migration
        ),
    ]
```

### Step 3: Update GameBoardTileState References

Create another migration to update `GameBoardTileState` to reference `BoardPosition`:

```python
# Create with: python manage.py makemigrations game --empty --name update_gameboardtilestate_refs

from django.db import migrations

def update_tile_state_references(apps, schema_editor):
    """Update GameBoardTileState to reference BoardPosition instead of BoardTile"""
    GameBoardTileState = apps.get_model('game', 'GameBoardTileState')
    BoardPosition = apps.get_model('game', 'BoardPosition')
    
    for state in GameBoardTileState.objects.filter(board_tile__isnull=False):
        # Find corresponding BoardPosition
        try:
            bp = BoardPosition.objects.get(
                board=state.board_tile.board,
                position=state.board_tile.position
            )
            state.board_position = bp
            state.save()
        except BoardPosition.DoesNotExist:
            print(f"Warning: No BoardPosition found for {state}")

class Migration(migrations.Migration):
    dependencies = [
        ('game', '0003_migrate_boardtile_to_boardposition'),
    ]

    operations = [
        migrations.RunPython(update_tile_state_references),
    ]
```

### Step 4: Clean Up Legacy Fields (Optional)

Once you're confident the migration is complete, you can remove the deprecated fields:

```python
# Future migration to remove legacy fields
class Migration(migrations.Migration):
    dependencies = [
        ('game', '0004_update_gameboardtilestate_refs'),
    ]

    operations = [
        # Make board_position required
        migrations.AlterField(
            model_name='gameboardtilestate',
            name='board_position',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='game_states',
                to='game.boardposition'
            ),
        ),
        # Remove legacy field
        migrations.RemoveField(
            model_name='gameboardtilestate',
            name='board_tile',
        ),
        # Optionally remove BoardTile model entirely if no longer needed
        # migrations.DeleteModel(name='BoardTile'),
    ]
```

## Using the Management Command

The `brokeio_seed_board` command helps initialize or re-initialize boards:

```bash
# Initialize a board (idempotent - safe to run multiple times)
python manage.py brokeio_seed_board --board-id=1

# Force re-initialization (clears existing positions)
python manage.py brokeio_seed_board --board-id=1 --force
```

This command:
- Creates `BoardPosition` entries for special positions (start, prison, vacation, go_to_prison)
- Auto-creates appropriate `Tile` instances for special positions
- Is idempotent: won't overwrite existing custom positions unless `--force` is used
- Uses transactions for safety

## Code Changes Required

### Creating Boards

**Before:**
```python
board = Board.objects.create(name="My Board", size=10)
# Manually create BoardTile entries
start_tile = Tile.objects.create(title="Start", tile_type=TileType.START)
BoardTile.objects.create(board=board, tile=start_tile, position=0)
```

**After:**
```python
board = Board.objects.create(name="My Board", size=10)
# Special positions are auto-created via signal
# Or manually call:
board.initialize_positions()
```

### Creating Property Tiles

**Before:**
```python
tile = Tile.objects.create(title="Park Place", tile_type=TileType.CITY)
city = City.objects.create(tile=tile, base_price=350)
BoardTile.objects.create(board=board, tile=tile, position=37)
```

**After:**
```python
tile = Tile.objects.create(title="Park Place", tile_type=TileType.CUSTOM)
city = City.objects.create(tile=tile, base_price=350)
BoardPosition.objects.create(board=board, city=city, position=37)
```

### Querying Board Positions

**Before:**
```python
positions = BoardTile.objects.filter(board=board).order_by('position')
for bt in positions:
    print(f"Position {bt.position}: {bt.tile.title}")
```

**After:**
```python
positions = BoardPosition.objects.filter(board=board).order_by('position')
for bp in positions:
    title = bp.tile.title if bp.tile else bp.city.tile.title
    print(f"Position {bp.position}: {title}")
```

## Validation

`BoardPosition` enforces validation at the model level:

```python
# This will raise ValidationError - both tile and city set
bp = BoardPosition(board=board, position=1, tile=tile, city=city)
bp.save()  # ❌ ValidationError

# This will raise ValidationError - neither tile nor city set
bp = BoardPosition(board=board, position=1)
bp.save()  # ❌ ValidationError

# This is valid
bp = BoardPosition(board=board, position=1, tile=tile)
bp.save()  # ✓ OK
```

## Backwards Compatibility

The refactor maintains backwards compatibility during the migration period:

1. `BoardTile` model remains in the codebase (marked as deprecated)
2. `GameBoardTileState` supports both `board_tile` and `board_position` references
3. `Game.initialize_board_state()` works with both schemas

Once migration is complete, you can remove legacy models and fields.

## Testing

All existing tests have been updated to work with the new schema. New tests added:

- `BoardPositionModelTest`: Tests creation, validation, and constraints
- `BoardInitializationTest`: Tests auto-initialization and idempotency
- `TileTypeTest`: Verifies CITY was removed and VACATION was added
- `GameBoardTileStateNewSchemaTest`: Tests new schema compatibility

Run tests:
```bash
python manage.py test game
```

## Rollback Plan

If you need to rollback:

1. The migration is reversible - run `python manage.py migrate game 0001_initial`
2. Legacy `BoardTile` model is preserved during migration
3. Both schemas can coexist temporarily

## Key Benefits

1. **Clearer Separation**: Tiles vs. Properties (Cities) are now distinct
2. **Better Validation**: Model-level enforcement of business rules
3. **Auto-Initialization**: Special positions are created automatically
4. **Idempotency**: Safe to re-run initialization without data loss
5. **Game Session Model**: Multiple games can share the same board definition
6. **Extensibility**: Easy to add new tile types without cluttering the Tile model
