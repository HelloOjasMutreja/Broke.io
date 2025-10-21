# Quick Start Guide for Testing Broke.io

This guide will help you quickly set up and start testing the Broke.io game with pre-populated test data.

## Initial Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Seed test data**:
   ```bash
   python manage.py seed_game_data
   ```

4. **Start the server**:
   ```bash
   python manage.py runserver
   ```

5. **Open your browser**:
   Navigate to `http://127.0.0.1:8000/`

## Test Credentials

All test accounts use the same password: **testpass123**

- **player1** - Participates in all games
- **player2** - Participates in 2 games  
- **player3** - Participates in 2 games
- **player4** - Participates in 1 game

## Quick Test Scenarios

### 1. Join and Start a Game (2 minutes)

1. Login as **player2**
2. Go to `/game/` (game lobby)
3. Click "Waiting Room Game"
4. Click "Start Game" (if 2+ players)
5. Click "Roll Dice" to play

### 2. Play an Active Game (3 minutes)

1. Login as **player1**
2. Go to `/game/`
3. Click "Active Game - Mid Battle"
4. Click "Roll Dice" 
5. Buy properties or end turn
6. Watch money and position update

### 3. Test 4-Player Game (5 minutes)

1. Login as **player1**
2. Go to `/game/`
3. Click "Full House - Ready to Start"
4. Click "Start Game"
5. Play through multiple turns with different players

### 4. Play Against AI (3 minutes)

1. Login as **player1**
2. Go to `/game/`
3. Click "Solo vs AI"
4. Test single-player features
5. See properties already owned by you and AI

## What's Pre-loaded

After running `seed_game_data`, you'll have:

✅ **3 boards** (Classic, Cyber City, Fantasy Realm)
✅ **120 tiles** (40 per board with prices, rent, special spaces)
✅ **4 games** (in different states: waiting, active, ready to start)
✅ **10 players** (4 human, 1 AI with realistic stats)
✅ **12 cities** (built on owned properties with varying levels, populations, and defenses)
✅ **27 cards** (Chance and Community Chest)
✅ **Game history** (turns, actions, chat messages)
✅ **Properties owned** (some games have properties already distributed)
✅ **PowerUps and Resources** (in active games)

## Admin Access

To view/edit data via Django admin:

1. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

2. Visit `http://127.0.0.1:8000/admin/`

3. Browse all game models

## Reset Test Data

To clear and reseed:

```bash
python manage.py seed_game_data --clear
```

## API Testing

Test these endpoints after seeding:

- **Game Lobby**: `GET /game/`
- **Game State**: `GET /game/2/state/` (Active game)
- **Game Detail**: `GET /game/2/` (Active game)

Example with curl:
```bash
curl http://localhost:8000/game/2/state/ | python -m json.tool
```

## Common Issues

**Issue**: "No module named django"
**Solution**: Run `pip install -r requirements.txt`

**Issue**: "Table doesn't exist"
**Solution**: Run `python manage.py migrate`

**Issue**: "No test data"
**Solution**: Run `python manage.py seed_game_data`

**Issue**: "Need to clear existing data"
**Solution**: Run `python manage.py seed_game_data --clear`

## Next Steps

- Read [TEST_DATA_REFERENCE.md](TEST_DATA_REFERENCE.md) for detailed info
- Check [GAME_SETUP.md](GAME_SETUP.md) for backend details
- See [README.md](README.md) for full game features

## Testing Checklist

- [ ] Login with test accounts
- [ ] View game lobby with 4 games
- [ ] Join a waiting game
- [ ] Start a game with 2+ players
- [ ] Roll dice and move
- [ ] Buy properties
- [ ] End turn
- [ ] View properties owned
- [ ] Test chat (if implemented)
- [ ] Test PowerUps (if implemented)
- [ ] Play through complete turn cycle
- [ ] Test all 3 board themes
- [ ] Verify AI player behavior (solo game)

Enjoy testing Broke.io! 🎲💰
