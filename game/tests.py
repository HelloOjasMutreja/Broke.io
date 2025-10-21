from django.test import TestCase
from django.contrib.auth.models import User
from .models import (
    Board, Game, Player, City, Tile, Resource,
    Action, Turn, Trade, PowerUp,
    ChatMessage, Auction, Bid, Card, Minigame, Transaction
)


class BoardModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(
            name="Test Board",
            width=11,
            height=11,
            theme="classic"
        )

    def test_board_creation(self):
        self.assertEqual(self.board.name, "Test Board")
        self.assertEqual(self.board.width, 11)
        self.assertEqual(self.board.height, 11)
        self.assertTrue(self.board.is_active)

    def test_board_str(self):
        self.assertEqual(str(self.board), "Test Board (11x11)")

    def test_get_total_tiles(self):
        self.assertEqual(self.board.get_total_tiles(), 121)


class GameModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", width=11, height=11)
        self.game = Game.objects.create(
            board=self.board,
            name="Test Game",
            mode="solo",
            max_players=4
        )

    def test_game_creation(self):
        self.assertEqual(self.game.name, "Test Game")
        self.assertEqual(self.game.mode, "solo")
        self.assertEqual(self.game.status, "waiting")
        self.assertEqual(self.game.max_players, 4)

    def test_game_str(self):
        self.assertIn("Test Game", str(self.game))
        self.assertIn("Solo", str(self.game))

    def test_can_start(self):
        # Game should not start with no players
        self.assertFalse(self.game.can_start())
        
        # Add two players
        user1 = User.objects.create_user(username="player1")
        user2 = User.objects.create_user(username="player2")
        Player.objects.create(game=self.game, user=user1, name="Player 1", turn_order=0, is_ready=False)
        Player.objects.create(game=self.game, user=user2, name="Player 2", turn_order=1, is_ready=False)
        
        # Game cannot start yet - players not ready
        self.assertFalse(self.game.can_start())
        
        # Mark both players as ready
        for player in self.game.players.all():
            player.is_ready = True
            player.save()
        
        # Now game can start
        self.assertTrue(self.game.can_start())


class PlayerModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", width=11, height=11)
        self.game = Game.objects.create(board=self.board, name="Test Game")
        self.user = User.objects.create_user(username="testuser")
        self.player = Player.objects.create(
            game=self.game,
            user=self.user,
            name="Test Player",
            money=1500,
            turn_order=0
        )

    def test_player_creation(self):
        self.assertEqual(self.player.name, "Test Player")
        self.assertEqual(self.player.money, 1500)
        self.assertEqual(self.player.level, 1)
        self.assertTrue(self.player.is_active)

    def test_add_money(self):
        self.player.add_money(500)
        self.assertEqual(self.player.money, 2000)

    def test_remove_money(self):
        self.player.remove_money(500)
        self.assertEqual(self.player.money, 1000)

    def test_add_experience(self):
        self.player.add_experience(150)
        self.assertEqual(self.player.experience, 150)
        self.assertEqual(self.player.level, 2)


class TileModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", width=11, height=11)
        self.game = Game.objects.create(board=self.board, name="Test Game")
        self.player = Player.objects.create(
            game=self.game,
            name="Test Player",
            turn_order=0
        )
        self.tile = Tile.objects.create(
            board=self.board,
            position=1,
            x_coordinate=10,
            y_coordinate=11,
            name="Test Property",
            terrain_type="property",
            price=100,
            rent=10
        )

    def test_tile_creation(self):
        self.assertEqual(self.tile.name, "Test Property")
        self.assertEqual(self.tile.position, 1)
        self.assertEqual(self.tile.price, 100)
        self.assertEqual(self.tile.rent, 10)

    def test_calculate_rent(self):
        # No rent without owner
        self.assertEqual(self.tile.calculate_rent(), 0)
        
        # Set owner
        self.tile.owner = self.player
        self.tile.save()
        
        # Base rent
        self.assertEqual(self.tile.calculate_rent(), 10)
        
        # With improvements
        self.tile.improvement_level = 1
        self.assertEqual(self.tile.calculate_rent(), 20)
        
        self.tile.improvement_level = 2
        self.assertEqual(self.tile.calculate_rent(), 40)


class CityModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", width=11, height=11)
        self.game = Game.objects.create(board=self.board, name="Test Game")
        self.player = Player.objects.create(
            game=self.game,
            name="Test Player",
            turn_order=0
        )
        self.tile = Tile.objects.create(
            board=self.board,
            position=1,
            x_coordinate=10,
            y_coordinate=11,
            name="Test Property",
            terrain_type="property",
            price=100,
            rent=10,
            owner=self.player
        )
        self.city = City.objects.create(
            tile=self.tile,
            player=self.player,
            name="Test City",
            level=1,
            population=100,
            defense=10,
            production_capacity=10,
            storage_capacity=100,
            health=100
        )

    def test_city_creation(self):
        self.assertEqual(self.city.name, "Test City")
        self.assertEqual(self.city.level, 1)
        self.assertEqual(self.city.population, 100)
        self.assertEqual(self.city.defense, 10)
        self.assertEqual(self.city.health, 100)
        self.assertFalse(self.city.is_capital)

    def test_city_str(self):
        self.assertIn("Test City", str(self.city))
        self.assertIn("Level 1", str(self.city))
        self.assertIn(self.player.name, str(self.city))

    def test_city_upgrade(self):
        initial_level = self.city.level
        initial_defense = self.city.defense
        initial_production = self.city.production_capacity
        initial_storage = self.city.storage_capacity
        
        self.city.upgrade()
        
        self.assertEqual(self.city.level, initial_level + 1)
        self.assertEqual(self.city.defense, initial_defense + 5)
        self.assertEqual(self.city.production_capacity, initial_production + 10)
        self.assertEqual(self.city.storage_capacity, initial_storage + 50)

    def test_city_upgrade_max_level(self):
        self.city.level = 10
        self.city.save()
        
        self.city.upgrade()
        
        # Should not exceed max level
        self.assertEqual(self.city.level, 10)

    def test_city_repair(self):
        self.city.health = 50
        self.city.save()
        
        self.city.repair(30)
        
        self.assertEqual(self.city.health, 80)

    def test_city_repair_max_health(self):
        self.city.health = 90
        self.city.save()
        
        self.city.repair(20)
        
        # Should not exceed max health
        self.assertEqual(self.city.health, 100)

    def test_capital_city(self):
        capital = City.objects.create(
            tile=self.tile,
            player=self.player,
            name="Capital",
            level=3,
            is_capital=True
        )
        
        self.assertTrue(capital.is_capital)
        self.assertEqual(capital.level, 3)


class ResourceModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", width=11, height=11)
        self.game = Game.objects.create(board=self.board, name="Test Game")
        self.player = Player.objects.create(
            game=self.game,
            name="Test Player",
            turn_order=0
        )
        self.resource = Resource.objects.create(
            player=self.player,
            resource_type="gold",
            amount=100,
            capacity=1000
        )

    def test_resource_creation(self):
        self.assertEqual(self.resource.resource_type, "gold")
        self.assertEqual(self.resource.amount, 100)

    def test_add_resource(self):
        self.resource.add(50)
        self.assertEqual(self.resource.amount, 150)

    def test_add_resource_with_capacity(self):
        self.resource.amount = 980
        self.resource.add(50)
        self.assertEqual(self.resource.amount, 1000)  # Capped at capacity

    def test_has_sufficient(self):
        self.assertTrue(self.resource.has_sufficient(50))
        self.assertFalse(self.resource.has_sufficient(150))


class TurnModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", width=11, height=11)
        self.game = Game.objects.create(board=self.board, name="Test Game")
        self.player = Player.objects.create(
            game=self.game,
            name="Test Player",
            turn_order=0
        )
        self.turn = Turn.objects.create(
            game=self.game,
            player=self.player,
            turn_number=1,
            round_number=1
        )

    def test_turn_creation(self):
        self.assertEqual(self.turn.turn_number, 1)
        self.assertEqual(self.turn.round_number, 1)
        self.assertEqual(self.turn.phase, "roll")
        self.assertFalse(self.turn.is_complete)

    def test_turn_str(self):
        self.assertIn("Turn 1", str(self.turn))
        self.assertIn("Round 1", str(self.turn))


class ActionModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", width=11, height=11)
        self.game = Game.objects.create(board=self.board, name="Test Game")
        self.player = Player.objects.create(
            game=self.game,
            name="Test Player",
            turn_order=0
        )
        self.turn = Turn.objects.create(
            game=self.game,
            player=self.player,
            turn_number=1,
            round_number=1
        )
        self.action = Action.objects.create(
            turn=self.turn,
            player=self.player,
            action_type="buy",
            amount=100
        )

    def test_action_creation(self):
        self.assertEqual(self.action.action_type, "buy")
        self.assertEqual(self.action.amount, 100)
        self.assertTrue(self.action.is_successful)


class PowerUpModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", width=11, height=11)
        self.game = Game.objects.create(board=self.board, name="Test Game")
        self.player = Player.objects.create(
            game=self.game,
            name="Test Player",
            turn_order=0
        )
        self.powerup = PowerUp.objects.create(
            player=self.player,
            powerup_type="double_rent",
            name="Double Rent",
            description="Doubles rent collected for 2 turns",
            duration=2
        )

    def test_powerup_creation(self):
        self.assertEqual(self.powerup.powerup_type, "double_rent")
        self.assertFalse(self.powerup.is_active)
        self.assertFalse(self.powerup.is_used)


class ChatAuctionExtrasTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Board", width=11, height=11)
        self.game = Game.objects.create(board=self.board, name="Game")
        self.p1 = Player.objects.create(game=self.game, name="P1", turn_order=0)
        self.p2 = Player.objects.create(game=self.game, name="P2", money=1000, turn_order=1)
        self.tile = Tile.objects.create(
            board=self.board, position=1, x_coordinate=0, y_coordinate=0,
            name="Tile1", terrain_type="property", price=100, rent=10
        )

    def test_chat_message_creation(self):
        msg = ChatMessage.objects.create(game=self.game, player=self.p1, message_type='player', content='Hello')
        self.assertEqual(msg.content, 'Hello')
        self.assertEqual(msg.player, self.p1)

    def test_auction_and_bid_flow(self):
        auction = Auction.objects.create(game=self.game, tile=self.tile, started_by=self.p1, starting_price=50)
        # First bid valid
        bid1 = auction.place_bid(bidder=self.p2, amount=60)
        self.assertIsInstance(bid1, Bid)
        self.assertEqual(auction.current_price, 60)
        self.assertEqual(auction.highest_bidder, self.p2)
        # End auction => transfer ownership and deduct money
        auction.end()
        self.tile.refresh_from_db()
        self.p2.refresh_from_db()
        self.assertEqual(self.tile.owner, self.p2)
        self.assertEqual(self.p2.money, 940)  # 1000 - 60

    def test_card_model(self):
        card = Card.objects.create(deck='chance', title='Bank pays you dividend of $50', effect={'money': 50})
        self.assertTrue(card.is_active)
        self.assertEqual(card.deck, 'chance')

    def test_minigame_complete(self):
        mg = Minigame.objects.create(game=self.game, player=self.p1, minigame_type='quick_math', score=10)
        mg.complete(reward=200)
        mg.refresh_from_db()
        self.p1.refresh_from_db()
        self.assertTrue(mg.is_completed)
        self.assertEqual(mg.reward, 200)
        self.assertEqual(self.p1.money, 1700)  # default 1500 + 200

    def test_transaction_record(self):
        act = Action.objects.create(
            turn=Turn.objects.create(game=self.game, player=self.p1, turn_number=1, round_number=1),
            player=self.p1, action_type='pay', amount=100
        )
        txn = Transaction.objects.create(
            game=self.game,
            from_player=self.p1,
            to_player=self.p2,
            kind='money',
            amount=100,
            reason='Rent',
            related_action=act
        )
        self.assertEqual(txn.amount, 100)
        self.assertEqual(txn.reason, 'Rent')


class GameWithCitiesTest(TestCase):
    def setUp(self):
        # Create board
        self.board = Board.objects.create(name="Test Board", width=11, height=11)
        
        # Create game
        self.game = Game.objects.create(
            board=self.board,
            name="Test Game with Cities",
            mode="friends",
            status="active"
        )
        
        # Create players
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        
        self.player1 = Player.objects.create(
            game=self.game,
            user=self.user1,
            name="Player 1",
            money=2000,
            turn_order=0
        )
        self.player2 = Player.objects.create(
            game=self.game,
            user=self.user2,
            name="Player 2",
            money=1500,
            turn_order=1
        )
        
        # Create tiles with owners
        self.tile1 = Tile.objects.create(
            board=self.board,
            position=1,
            x_coordinate=9,
            y_coordinate=10,
            name="Property 1",
            terrain_type="property",
            price=200,
            rent=20,
            owner=self.player1
        )
        self.tile2 = Tile.objects.create(
            board=self.board,
            position=3,
            x_coordinate=7,
            y_coordinate=10,
            name="Property 2",
            terrain_type="property",
            price=300,
            rent=30,
            owner=self.player2
        )

    def test_game_with_multiple_cities(self):
        """Test creating a game with multiple cities"""
        city1 = City.objects.create(
            tile=self.tile1,
            player=self.player1,
            name="New York",
            level=2,
            population=200,
            is_capital=True
        )
        city2 = City.objects.create(
            tile=self.tile2,
            player=self.player2,
            name="London",
            level=1,
            population=150
        )
        
        # Verify cities are created
        self.assertEqual(City.objects.filter(player=self.player1).count(), 1)
        self.assertEqual(City.objects.filter(player=self.player2).count(), 1)
        
        # Verify city attributes
        self.assertTrue(city1.is_capital)
        self.assertFalse(city2.is_capital)
        self.assertEqual(city1.level, 2)
        self.assertEqual(city2.level, 1)

    def test_city_ownership_matches_tile_owner(self):
        """Test that city owner matches tile owner"""
        city = City.objects.create(
            tile=self.tile1,
            player=self.player1,
            name="Test City",
            level=1
        )
        
        self.assertEqual(city.player, self.tile1.owner)

    def test_multiple_upgrades(self):
        """Test upgrading a city multiple times"""
        city = City.objects.create(
            tile=self.tile1,
            player=self.player1,
            name="Growing City",
            level=1,
            defense=10,
            production_capacity=10,
            storage_capacity=100
        )
        
        # Upgrade 3 times
        for _ in range(3):
            city.upgrade()
        
        self.assertEqual(city.level, 4)
        self.assertEqual(city.defense, 25)  # 10 + 3*5
        self.assertEqual(city.production_capacity, 40)  # 10 + 3*10
        self.assertEqual(city.storage_capacity, 250)  # 100 + 3*50

    def test_player_with_multiple_cities(self):
        """Test a player owning multiple cities"""
        # Create additional tiles for player 1
        tile3 = Tile.objects.create(
            board=self.board,
            position=5,
            x_coordinate=5,
            y_coordinate=10,
            name="Property 3",
            terrain_type="property",
            price=250,
            rent=25,
            owner=self.player1
        )
        
        # Create multiple cities for player 1
        City.objects.create(tile=self.tile1, player=self.player1, name="City A", level=2)
        City.objects.create(tile=tile3, player=self.player1, name="City B", level=1)
        
        # Verify player has 2 cities
        player_cities = City.objects.filter(player=self.player1)
        self.assertEqual(player_cities.count(), 2)
        
        # Verify total levels
        total_levels = sum(city.level for city in player_cities)
        self.assertEqual(total_levels, 3)


class ViewTestCase(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        
        # Create board
        self.board = Board.objects.create(name="Test Board", width=11, height=11)
        
        # Create tiles
        for i in range(10):
            Tile.objects.create(
                board=self.board,
                position=i,
                x_coordinate=i,
                y_coordinate=0,
                name=f"Tile {i}",
                terrain_type="property" if i > 0 else "special",
                price=100 * i if i > 0 else 0,
                rent=10 * i if i > 0 else 0
            )
    
    def test_game_lobby_view(self):
        """Test game lobby displays games"""
        response = self.client.get('/game/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/lobby.html')
    
    def test_create_game_requires_login(self):
        """Test that creating a game requires login"""
        response = self.client.post('/game/create/', {
            'board_id': self.board.id,
            'game_name': 'Test Game',
            'game_mode': 'friends',
            'max_players': 4
        })
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/users/login'))
    
    def test_create_game_authenticated(self):
        """Test creating a game when authenticated"""
        self.client.login(username='user1', password='pass123')
        response = self.client.post('/game/create/', {
            'board_id': self.board.id,
            'game_name': 'Test Game',
            'game_mode': 'friends',
            'max_players': 4
        })
        # Should redirect to game detail
        self.assertEqual(response.status_code, 302)
        
        # Check game was created
        game = Game.objects.filter(name='Test Game').first()
        self.assertIsNotNone(game)
        self.assertEqual(game.mode, 'friends')
        
        # Check player was added
        player = game.players.filter(user=self.user1).first()
        self.assertIsNotNone(player)
    
    def test_game_detail_view(self):
        """Test game detail view"""
        # Create game
        game = Game.objects.create(
            board=self.board,
            name='Test Game',
            mode='friends',
            status='waiting'
        )
        
        response = self.client.get(f'/game/{game.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/game_detail.html')
        self.assertEqual(response.context['game'], game)
    
    def test_start_game_requires_login(self):
        """Test starting game requires login"""
        game = Game.objects.create(
            board=self.board,
            name='Test Game',
            mode='friends',
            status='waiting'
        )
        
        response = self.client.post(f'/game/{game.id}/start/')
        self.assertEqual(response.status_code, 302)
    
    def test_start_game(self):
        """Test starting a game"""
        self.client.login(username='user1', password='pass123')
        
        # Create game with 2 players, user1 as owner
        game = Game.objects.create(
            board=self.board,
            owner=self.user1,
            name='Test Game',
            mode='friends',
            status='waiting'
        )
        player1 = Player.objects.create(game=game, user=self.user1, name='User1', turn_order=0, is_ready=True)
        player2 = Player.objects.create(game=game, user=self.user2, name='User2', turn_order=1, is_ready=True)
        
        response = self.client.post(f'/game/{game.id}/start/')
        self.assertEqual(response.status_code, 200)
        
        # Check response
        data = response.json()
        self.assertTrue(data['success'])
        
        # Check game status changed
        game.refresh_from_db()
        self.assertEqual(game.status, 'active')
        
        # Check first turn was created
        turn = Turn.objects.filter(game=game).first()
        self.assertIsNotNone(turn)
        self.assertEqual(turn.turn_number, 1)
    
    def test_roll_dice(self):
        """Test rolling dice"""
        self.client.login(username='user1', password='pass123')
        
        # Create active game
        game = Game.objects.create(
            board=self.board,
            name='Test Game',
            mode='friends',
            status='active'
        )
        player = Player.objects.create(game=game, user=self.user1, name='User1', turn_order=0)
        
        # Create turn
        turn = Turn.objects.create(
            game=game,
            player=player,
            turn_number=1,
            round_number=1,
            phase='roll'
        )
        
        response = self.client.post(f'/game/{game.id}/roll-dice/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('dice1', data)
        self.assertIn('dice2', data)
        self.assertIn('total', data)
        self.assertEqual(data['total'], data['dice1'] + data['dice2'])
        
        # Check turn was updated
        turn.refresh_from_db()
        self.assertEqual(turn.phase, 'action')
        self.assertIsNotNone(turn.dice_roll)
        
        # Check action was recorded
        action = Action.objects.filter(turn=turn, action_type='roll_dice').first()
        self.assertIsNotNone(action)
    
    def test_game_state_json(self):
        """Test game state JSON endpoint"""
        # Create game with players
        game = Game.objects.create(
            board=self.board,
            name='Test Game',
            mode='friends',
            status='active'
        )
        player1 = Player.objects.create(game=game, user=self.user1, name='User1', turn_order=0, money=1500)
        player2 = Player.objects.create(game=game, user=self.user2, name='User2', turn_order=1, money=1500)
        
        response = self.client.get(f'/game/{game.id}/state/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('game', data)
        self.assertIn('players', data)
        self.assertEqual(len(data['players']), 2)
        self.assertEqual(data['game']['id'], game.id)
        self.assertEqual(data['game']['status'], 'active')
