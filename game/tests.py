from django.test import TestCase
from django.contrib.auth.models import User
from .models import (
    Board, Game, Player, City, Tile, Resource,
    Action, Turn, Trade, PowerUp
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
        Player.objects.create(game=self.game, user=user1, name="Player 1", turn_order=0)
        Player.objects.create(game=self.game, user=user2, name="Player 2", turn_order=1)
        
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
