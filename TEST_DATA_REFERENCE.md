# Game Test Data Reference

This document describes the test data created by the `seed_game_data` management command.

## Overview

The seed command creates a complete test environment for the Broke.io game, including:
- 3 themed boards with 40 tiles each
- 4 games in different states
- 10 players (human and AI)
- 27 cards (Chance and Community Chest)
- Sample game history (turns, actions, transactions)
- PowerUps, resources, and chat messages

## Test User Accounts

All test users have the same password: `testpass123`

| Username | Email | Notes |
|----------|-------|-------|
| player1 | player1@example.com | Participates in all games |
| player2 | player2@example.com | Participates in 2 games |
| player3 | player3@example.com | Participates in 2 games |
| player4 | player4@example.com | Participates in 1 game |

## Boards Created

### 1. Classic Board
- **Theme**: classic
- **Size**: 11x11 (40 tiles)
- **Description**: Traditional Monopoly-style board
- **Tiles**: Includes GO, Jail, Free Parking, properties with color groups (brown, light blue, pink, orange, red, yellow, green, dark blue), railroads, and utilities

### 2. Cyber City
- **Theme**: cyber
- **Size**: 11x11 (40 tiles)
- **Description**: Futuristic neon-themed board
- **Tiles**: Themed spaces with sci-fi names

### 3. Fantasy Realm
- **Theme**: fantasy
- **Size**: 11x11 (40 tiles)
- **Description**: Magical fantasy-themed board
- **Tiles**: Themed spaces with fantasy names

## Games Created

### 1. Waiting Room Game
- **Status**: waiting (needs more players to start)
- **Mode**: friends
- **Board**: Classic Board
- **Players**: 1 (player1)
- **Max Players**: 4
- **Starting Money**: $1500
- **Use Case**: Test joining a game that's waiting for players

### 2. Active Game - Mid Battle
- **Status**: active (game in progress)
- **Mode**: friends
- **Board**: Classic Board
- **Players**: 3 (player1, player2, player3)
- **Current Turn**: Round 3, ready to roll dice
- **Use Case**: Test mid-game features, property ownership, turns
- **Special Features**:
  - Players have different money amounts ($1200-$1800)
  - 15 properties distributed among players
  - Some properties have improvements (1-2 levels)
  - 7 completed turns with actions
  - 1 active turn waiting for dice roll
  - 2 PowerUps (Double Rent, Rent Shield)
  - Resources for all players
  - 4 chat messages
  - 1 completed minigame
  - 1 transaction record

### 3. Full House - Ready to Start
- **Status**: waiting (ready to start with max players)
- **Mode**: friends
- **Board**: Cyber City
- **Players**: 4 (player1, player2, player3, player4)
- **Max Players**: 4 (full)
- **Starting Money**: $1500
- **Use Case**: Test starting a full game
- **Player Tokens**: 🚗, 🚢, 🎩, 🐕

### 4. Solo vs AI
- **Status**: active (game in progress)
- **Mode**: solo
- **Board**: Classic Board
- **Players**: 2 (player1, AI Bot)
- **Use Case**: Test AI gameplay and solo mode
- **Special Features**:
  - 5 properties owned (3 by player1, 2 by AI Bot)
  - Players at different positions (15 and 8)
  - Different money amounts ($1200 and $1400)

## Cards Created

### Chance Cards (11 total)
- Advance to GO (collect $200)
- Bank pays you dividend ($50)
- Go Back 3 Spaces
- Go to Jail
- Make general repairs ($25 per house, $100 per hotel)
- Pay poor tax ($15)
- Take a trip to Reading Railroad
- Advance to Boardwalk
- You have been elected Chairman (pay each player $50)
- Building loan matures (collect $150)
- Get out of Jail Free

### Community Chest Cards (16 total)
- Advance to GO (collect $200)
- Bank error in your favor ($200)
- Doctor's fees (pay $50)
- From sale of stock (get $50)
- Get out of Jail Free
- Go to Jail
- Grand Opera Night (collect $50 from every player)
- Holiday Fund matures ($100)
- Income tax refund ($20)
- Life insurance matures ($100)
- Pay hospital fees ($100)
- Pay school fees ($50)
- Receive $25 consultancy fee
- Street repairs ($40 per house, $115 per hotel)
- You have won second prize in beauty contest ($10)
- You inherit $100

## Testing Scenarios

### Scenario 1: Join a Game
1. Login as player2, player3, or player4
2. Navigate to `/game/`
3. Join "Waiting Room Game"
4. Once 2+ players, start the game

### Scenario 2: Play an Active Game
1. Login as player1, player2, or player3
2. Navigate to `/game/`
3. Join "Active Game - Mid Battle"
4. Roll dice, move, buy properties, end turn

### Scenario 3: Start a Full Game
1. Login as player1
2. Navigate to `/game/`
3. Click on "Full House - Ready to Start"
4. Start the game
5. Play through turns with 4 players

### Scenario 4: Play Against AI
1. Login as player1
2. Navigate to `/game/`
3. Join "Solo vs AI"
4. Test single-player gameplay against AI

### Scenario 5: Create New Game
1. Login with any account
2. Navigate to `/game/`
3. Create a new game
4. Select board (Classic, Cyber City, or Fantasy Realm)
5. Choose game mode and max players

## Clearing and Re-seeding

To clear all game data and reseed:

```bash
python manage.py seed_game_data --clear
```

This will:
1. Delete all existing game data (boards, games, players, etc.)
2. Recreate all test data from scratch
3. Preserve user accounts (won't delete users)

## Database Statistics

After seeding, the database contains:
- **Boards**: 3
- **Tiles**: 120 (40 per board)
- **Games**: 4
- **Players**: 10
- **Cards**: 27
- **PowerUps**: 2
- **Chat Messages**: 4
- **Minigames**: 1
- **Turns**: 8 (7 completed, 1 active)
- **Actions**: ~16 (2 per turn)
- **Transactions**: 1
- **Resources**: 3 (1 per player in active game)

## API Endpoints to Test

After seeding, test these endpoints:

1. **Game Lobby**: `GET /game/`
2. **Game State**: `GET /game/{game_id}/state/`
3. **Game Detail**: `GET /game/{game_id}/`
4. **Create Game**: `POST /game/create/`
5. **Join Game**: `POST /game/{game_id}/join/`
6. **Start Game**: `POST /game/{game_id}/start/`
7. **Roll Dice**: `POST /game/{game_id}/roll-dice/`
8. **Buy Property**: `POST /game/{game_id}/buy-property/`
9. **End Turn**: `POST /game/{game_id}/end-turn/`

## Admin Interface

All seeded data can be viewed and edited in the Django admin:

1. Create superuser: `python manage.py createsuperuser`
2. Navigate to: `http://localhost:8000/admin/`
3. Browse models: Boards, Games, Players, Tiles, Cards, etc.

## Notes

- All monetary values are in the game's currency
- Starting money is $1500 per player by default
- Property prices range from $60 to $400
- Rent ranges from $2 to $50 depending on property value
- Player positions range from 0-39 on the board
- The seed data is designed to test all major game features
