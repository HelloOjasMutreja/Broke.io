# Model Migration Guide

This document describes the changes made to the game models to align with the monopoly-inspired game design reference.

## Overview

The models have been completely restructured to better support a monopoly-inspired board game with proper separation of concerns and reusability.

## Major Changes

### 1. Board Model
**Before:**
- Used `width` and `height` for board dimensions
- Simple validation

**After:**
- Uses `size` parameter (n×n board)
- Added `total_tiles` property
- Added `default_special_positions()` method to define special tile positions:
  - 0 → Start
  - (n-1) → Prison
  - (2n-1) → Vacation
  - (3n-1) → Go to Prison

### 2. Tile System (New Architecture)
**Before:**
- Tiles were bound to boards
- Ownership tracked directly on Tile
- Mixed canonical and instance data

**After:**
Three-model system for better reusability:

#### Tile (Canonical)
- Reusable tile definitions
- Contains tile type, description, action metadata
- Can be used across multiple boards

#### BoardTile (Instance)
- Maps Tiles to specific positions on a Board
- Allows same Tile to appear multiple times
- Supports position-specific overrides

#### GameBoardTileState (Per-Game State)
- Tracks ownership, houses, mortgage status per game
- Allows same board to be used in multiple games
- Keeps game state isolated

### 3. City Model
**Before:**
- Separate entity with reference to Tile
- Mixed gameplay and property data

**After:**
- OneToOne relationship with Tile
- Explicit rent structure (base, house 1-4, hotel)
- Clear property pricing (base_price, mortgage_value)
- House/hotel costs defined
- Color groups for monopoly sets

### 4. Game Model
**Before:**
- Simple status tracking
- Limited lobby functionality

**After:**
- Dual identifiers: `uuid` (internal) and `public_id` (human-friendly)
- GameStatus enum (LOBBY, READY, ACTIVE, PAUSED, FINISHED)
- Built-in lobby logic with `can_start()` and `all_players_ready()`
- Atomic `start()` method with proper initialization
- `initialize_board_state()` creates per-game tile states

### 5. Player System (Split)
**Before:**
- Single Player model tied to games
- Mixed persistent and session data

**After:**
Two-model system:

#### Player (Persistent)
- User identity across games
- Can be linked to User or be AI
- Reusable entity

#### LobbyPlayer (Game-Specific)
- Per-game player state
- Cash, position, ready status
- Seat assignment
- Owner flag

### 6. Turn Model
**Before:**
- Complex turn tracking
- Phase management
- Action history

**After:**
- Simplified to track current turn only
- Just game, player, and round number
- Cleaner state management

### 7. ActionLog (Replaced Action)
**Before:**
- Action model with multiple relations

**After:**
- ActionLog for audit trail
- JSON payload for flexibility
- Simple action_type string
- Chronological ordering

### 8. Trade Model
**Before:**
- Complex offer/request structure

**After:**
- Flexible JSON-based offers
- `offered` and `requested` as JSON fields
- Nullable `accepted` (None=pending, True=accepted, False=rejected)

### 9. Bid Model
**Before:**
- Complex auction system

**After:**
- References GameBoardTileState
- Simple amount tracking
- Ties to specific game and player

### 10. ChatMessage Model
**Before:**
- Player-only messages

**After:**
- Added `is_system` flag
- Supports both player and system messages
- Player can be null for system messages

## Removed Models

The following models were removed as they weren't part of the reference design:
- **Resource** - Resource management system
- **PowerUp** - Special abilities system
- **Auction** - Complex auction mechanics (simplified to Bid)
- **Card** - Chance/Community Chest cards
- **Minigame** - Mini-game system
- **Transaction** - Complex transaction tracking (replaced by ActionLog)

## Migration Steps

To use the new models:

1. **Clear old database:**
   ```bash
   rm db.sqlite3
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Seed test data:**
   ```bash
   python manage.py seed_game_data
   ```

4. **Test credentials:**
   - Username: player1-4
   - Password: testpass123

## Testing

All tests have been updated to work with the new model structure:
- 36 comprehensive tests covering all models
- Tests include model creation, relationships, constraints, and game flow
- All tests pass successfully
- No security vulnerabilities detected

## Admin Interface

The admin interface has been updated to work with all new models, providing easy management of:
- Boards and Tiles
- BoardTiles (tile placement)
- Cities (property data)
- Games and Players
- LobbyPlayers (game participants)
- GameBoardTileStates (tile ownership)
- Turns, ActionLogs, Trades, Bids, and ChatMessages

## Key Benefits

1. **Better Separation of Concerns**: Canonical data (Tiles) separated from instance data (BoardTiles) and game state (GameBoardTileState)

2. **Reusability**: Tiles and Boards can be reused across multiple games

3. **Flexibility**: JSON fields allow for extensible game mechanics without schema changes

4. **Scalability**: Per-game state isolation allows multiple games to run simultaneously with the same board

5. **Maintainability**: Cleaner, more focused models that each handle one responsibility

6. **Testing**: Comprehensive test coverage ensures reliability
