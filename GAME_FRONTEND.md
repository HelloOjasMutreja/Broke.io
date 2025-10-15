# Game Frontend Documentation

## Overview

The frontend has been remade to integrate with the Django backend, supporting multiple concurrent games, player turns, and game state persistence.

## Architecture

### URL Structure

- `/game/` - Game lobby (list all games, create new games)
- `/game/<id>/` - Game detail page (play the game)
- `/game/<id>/start/` - Start a game (API)
- `/game/<id>/roll-dice/` - Roll dice (API)
- `/game/<id>/buy-property/` - Buy property (API)
- `/game/<id>/end-turn/` - End turn (API)
- `/game/<id>/state/` - Get game state as JSON (API)

### Key Features

#### 1. Multiple Concurrent Games
- Game lobby shows all active and waiting games
- Players can create new games with custom settings
- Games are isolated - each has its own state and players

#### 2. Player Turns and Actions
- Turn-based gameplay with distinct phases:
  - **Roll Phase**: Player rolls two dice
  - **Move Phase**: Player moves based on dice roll
  - **Action Phase**: Player can buy property or perform other actions
  - **End Phase**: Player ends turn, next player begins
- All actions are recorded in the Action model for history/replay

#### 3. Game State Tracking
- Real-time game state updates via JSON API
- Auto-polling every 5 seconds to keep UI in sync
- State includes:
  - Current turn and round numbers
  - Player positions, money, and stats
  - Tile ownership
  - Active player indication

#### 4. Persistence
- All game data stored in Django models
- Games can be paused and resumed
- Action history preserved for auditing

## Usage

### Starting a New Game

1. Navigate to `/game/` (Game Lobby)
2. Fill in the "Create New Game" form:
   - Game Name
   - Board (select from available boards)
   - Game Mode (Solo, Friends, Online)
   - Max Players (2-8)
3. Click "Create Game"
4. You'll be redirected to the game waiting room
5. Wait for other players to join (or add them manually)
6. Click "Start Game" when ready

### Playing the Game

1. When it's your turn, the "Roll Dice" button will be enabled
2. Click "Roll Dice" to roll two dice and move
3. If you land on a property, click "Buy Property" to purchase it
4. Click "End Turn" to complete your turn
5. Wait for other players to take their turns
6. The UI updates automatically via polling

## API Endpoints

### Roll Dice
```
POST /game/<game_id>/roll-dice/
Response: {
  "success": true,
  "dice1": 3,
  "dice2": 5,
  "total": 8,
  "new_position": 8,
  "passed_go": false,
  "money": 1500
}
```

### Buy Property
```
POST /game/<game_id>/buy-property/
Response: {
  "success": true,
  "tile_name": "Mediterranean Avenue",
  "price": 60,
  "remaining_money": 1440
}
```

### End Turn
```
POST /game/<game_id>/end-turn/
Response: {
  "success": true,
  "next_player_name": "Player 2",
  "next_turn_number": 2,
  "next_round_number": 1
}
```

### Game State
```
GET /game/<game_id>/state/
Response: {
  "game": {
    "id": 1,
    "name": "Test Game",
    "status": "active",
    "mode": "friends",
    "max_players": 4,
    "current_players": 2
  },
  "players": [
    {
      "id": 1,
      "name": "Player 1",
      "money": 1500,
      "position": 0,
      "turn_order": 0,
      "level": 1,
      "experience": 0,
      "score": 0
    }
  ],
  "current_turn": {
    "turn_number": 1,
    "round_number": 1,
    "phase": "roll",
    "player_id": 1,
    "player_name": "Player 1",
    "dice_roll": null
  },
  "tiles": [...]
}
```

## Frontend Components

### Templates

#### `templates/game/lobby.html`
- Displays available games
- Create game form
- Responsive two-column layout
- Beautiful gradient background

#### `templates/game/game_detail.html`
- Three-panel layout:
  - Left: Player list with stats
  - Center: Game board and controls
  - Right: Recent actions log
- Real-time updates via JavaScript polling
- Interactive buttons that enable/disable based on turn state
- Animated dice rolls

### JavaScript Features

- CSRF token handling for POST requests
- Automatic game state polling
- Dynamic UI updates without page refresh
- Message notifications for actions
- Button state management based on turn phase

## Testing

Run tests with:
```bash
python manage.py test game
```

Current test coverage: 28 tests covering:
- Model functionality
- View responses
- Game creation and joining
- Turn management
- Action recording
- API endpoints

## Future Enhancements

1. **WebSocket Support**: Replace polling with real-time WebSocket connections
2. **Animations**: Add visual board with property animations
3. **Trading System**: Implement player-to-player trading
4. **Power-ups**: Add special ability usage
5. **Chat System**: Real-time chat between players
6. **Spectator Mode**: Allow users to watch ongoing games
7. **Game Replay**: Replay games from action history
8. **Tournaments**: Multi-game tournament support
