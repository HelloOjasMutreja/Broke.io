from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import (
    Board, Tile, BoardTile, City, Game, Player, LobbyPlayer,
    GameBoardTileState, Turn, ActionLog, Trade, Bid, ChatMessage,
    GameStatus, TileType
)


class BoardModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(
            name="Test Board",
            size=10,
            theme="classic",
            description="A test board"
        )

    def test_board_creation(self):
        """Test board is created with correct attributes"""
        self.assertEqual(self.board.name, "Test Board")
        self.assertEqual(self.board.size, 10)
        self.assertEqual(self.board.theme, "classic")

    def test_board_str(self):
        """Test board string representation"""
        self.assertEqual(str(self.board), "Test Board (10x10)")

    def test_total_tiles_property(self):
        """Test total_tiles property returns correct value"""
        self.assertEqual(self.board.total_tiles, 100)

    def test_default_special_positions(self):
        """Test default_special_positions method"""
        positions = self.board.default_special_positions()
        self.assertEqual(positions["start"], 0)
        self.assertEqual(positions["prison"], 9)  # n-1
        self.assertEqual(positions["vacation"], 19)  # 2n-1
        self.assertEqual(positions["go_to_prison"], 29)  # 3n-1


class TileModelTest(TestCase):
    def setUp(self):
        self.tile = Tile.objects.create(
            title="Mediterranean Avenue",
            tile_type=TileType.CITY,
            description="A property tile",
            action={"type": "property", "buyable": True},
            metadata={"color": "brown"}
        )

    def test_tile_creation(self):
        """Test tile is created correctly"""
        self.assertEqual(self.tile.title, "Mediterranean Avenue")
        self.assertEqual(self.tile.tile_type, TileType.CITY)
        self.assertTrue(self.tile.action["buyable"])

    def test_tile_str(self):
        """Test tile string representation"""
        self.assertEqual(str(self.tile), "Mediterranean Avenue [CITY]")


class BoardTileModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", size=10)
        self.tile = Tile.objects.create(title="GO", tile_type=TileType.START)
        self.board_tile = BoardTile.objects.create(
            board=self.board,
            tile=self.tile,
            position=0
        )

    def test_board_tile_creation(self):
        """Test BoardTile is created correctly"""
        self.assertEqual(self.board_tile.position, 0)
        self.assertEqual(self.board_tile.board, self.board)
        self.assertEqual(self.board_tile.tile, self.tile)

    def test_board_tile_str(self):
        """Test BoardTile string representation"""
        self.assertEqual(str(self.board_tile), "Test Board @ 0 -> GO")

    def test_unique_position_constraint(self):
        """Test that same position cannot be used twice on same board"""
        with self.assertRaises(Exception):
            BoardTile.objects.create(
                board=self.board,
                tile=self.tile,
                position=0
            )


class CityModelTest(TestCase):
    def setUp(self):
        self.tile = Tile.objects.create(
            title="Boardwalk",
            tile_type=TileType.CITY
        )
        self.city = City.objects.create(
            tile=self.tile,
            country="USA",
            base_price=400,
            mortgage_value=200,
            rent_base=50,
            rent_house_1=200,
            rent_house_2=600,
            rent_house_3=1400,
            rent_house_4=1700,
            rent_hotel=2000,
            house_cost=200,
            hotel_cost=200,
            color_group="Dark Blue"
        )

    def test_city_creation(self):
        """Test City is created correctly"""
        self.assertEqual(self.city.base_price, 400)
        self.assertEqual(self.city.color_group, "Dark Blue")
        self.assertEqual(self.city.rent_hotel, 2000)

    def test_city_str(self):
        """Test City string representation"""
        self.assertEqual(str(self.city), "City: Boardwalk (400)")

    def test_onetoone_with_tile(self):
        """Test that only one City can be attached to a Tile"""
        with self.assertRaises(Exception):
            City.objects.create(tile=self.tile, base_price=100)


class GameModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", size=10)
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.game = Game.objects.create(
            board=self.board,
            owner=self.user,
            name="Test Game",
            max_players=4
        )

    def test_game_creation(self):
        """Test Game is created with correct defaults"""
        self.assertEqual(self.game.name, "Test Game")
        self.assertEqual(self.game.status, GameStatus.LOBBY)
        self.assertEqual(self.game.max_players, 4)
        self.assertIsNotNone(self.game.uuid)
        self.assertIsNotNone(self.game.public_id)

    def test_game_str(self):
        """Test Game string representation"""
        self.assertIn(self.game.public_id, str(self.game))
        self.assertIn("LOBBY", str(self.game))

    def test_all_players_ready_empty(self):
        """Test all_players_ready returns False when no players"""
        self.assertFalse(self.game.all_players_ready())

    def test_can_start_requires_owner(self):
        """Test that only owner can start game"""
        other_user = User.objects.create_user(username="other", password="pass123")
        self.assertFalse(self.game.can_start(other_user))
        self.assertFalse(self.game.can_start(self.user))  # Not enough players


class PlayerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player1", password="pass123")
        self.player = Player.objects.create(
            user=self.user,
            display_name="Player One",
            is_ai=False
        )

    def test_player_creation(self):
        """Test Player is created correctly"""
        self.assertEqual(self.player.display_name, "Player One")
        self.assertFalse(self.player.is_ai)
        self.assertEqual(self.player.user, self.user)

    def test_player_str(self):
        """Test Player string representation"""
        self.assertEqual(str(self.player), "Player One")

    def test_ai_player(self):
        """Test creating an AI player without user"""
        ai_player = Player.objects.create(
            display_name="AI Bot",
            is_ai=True
        )
        self.assertIsNone(ai_player.user)
        self.assertTrue(ai_player.is_ai)


class LobbyPlayerModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", size=10)
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.game = Game.objects.create(board=self.board, owner=self.user, name="Test Game")
        self.player = Player.objects.create(user=self.user, display_name="Test Player")
        self.lobby_player = LobbyPlayer.objects.create(
            game=self.game,
            player=self.player,
            seat_index=0,
            cash=1500,
            is_ready=False,
            is_owner=True
        )

    def test_lobby_player_creation(self):
        """Test LobbyPlayer is created correctly"""
        self.assertEqual(self.lobby_player.cash, 1500)
        self.assertEqual(self.lobby_player.seat_index, 0)
        self.assertFalse(self.lobby_player.is_ready)
        self.assertTrue(self.lobby_player.is_owner)

    def test_lobby_player_str(self):
        """Test LobbyPlayer string representation"""
        self.assertIn("Test Player", str(self.lobby_player))
        self.assertIn(self.game.public_id, str(self.lobby_player))

    def test_unique_seat_constraint(self):
        """Test that same seat cannot be used twice in same game"""
        player2 = Player.objects.create(display_name="Player 2")
        with self.assertRaises(Exception):
            LobbyPlayer.objects.create(
                game=self.game,
                player=player2,
                seat_index=0  # Same seat
            )


class GameBoardTileStateModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", size=10)
        self.tile = Tile.objects.create(title="Property", tile_type=TileType.CITY)
        self.board_tile = BoardTile.objects.create(
            board=self.board,
            tile=self.tile,
            position=5
        )
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.game = Game.objects.create(board=self.board, owner=self.user)
        self.player = Player.objects.create(display_name="Test Player")
        self.tile_state = GameBoardTileState.objects.create(
            game=self.game,
            board_tile=self.board_tile,
            position=5,
            owner=self.player,
            houses=2,
            mortgaged=False
        )

    def test_tile_state_creation(self):
        """Test GameBoardTileState is created correctly"""
        self.assertEqual(self.tile_state.houses, 2)
        self.assertEqual(self.tile_state.owner, self.player)
        self.assertFalse(self.tile_state.mortgaged)

    def test_tile_state_str(self):
        """Test GameBoardTileState string representation"""
        self.assertIn("Property", str(self.tile_state))
        self.assertIn(str(5), str(self.tile_state))


class TurnModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", size=10)
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.game = Game.objects.create(board=self.board, owner=self.user)
        self.player = Player.objects.create(display_name="Test Player")
        self.turn = Turn.objects.create(
            game=self.game,
            current_player=self.player,
            round_number=1
        )

    def test_turn_creation(self):
        """Test Turn is created correctly"""
        self.assertEqual(self.turn.round_number, 1)
        self.assertEqual(self.turn.current_player, self.player)

    def test_turn_str(self):
        """Test Turn string representation"""
        self.assertIn(self.game.public_id, str(self.turn))
        self.assertIn("Round 1", str(self.turn))


class ActionLogModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", size=10)
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.game = Game.objects.create(board=self.board, owner=self.user)
        self.player = Player.objects.create(display_name="Test Player")
        self.action = ActionLog.objects.create(
            game=self.game,
            player=self.player,
            action_type="roll_dice",
            payload={"dice1": 3, "dice2": 5}
        )

    def test_action_log_creation(self):
        """Test ActionLog is created correctly"""
        self.assertEqual(self.action.action_type, "roll_dice")
        self.assertEqual(self.action.payload["dice1"], 3)


class TradeModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", size=10)
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.game = Game.objects.create(board=self.board, owner=self.user)
        self.player1 = Player.objects.create(display_name="Player 1")
        self.player2 = Player.objects.create(display_name="Player 2")
        self.trade = Trade.objects.create(
            game=self.game,
            offered_by=self.player1,
            offered_to=self.player2,
            offered={"cash": 100, "tiles": [1, 2]},
            requested={"cash": 200, "tiles": [5]},
            accepted=None
        )

    def test_trade_creation(self):
        """Test Trade is created correctly"""
        self.assertEqual(self.trade.offered["cash"], 100)
        self.assertEqual(self.trade.requested["cash"], 200)
        self.assertIsNone(self.trade.accepted)

    def test_trade_acceptance(self):
        """Test updating trade acceptance"""
        self.trade.accepted = True
        self.trade.save()
        self.assertTrue(self.trade.accepted)


class BidModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", size=10)
        self.tile = Tile.objects.create(title="Property", tile_type=TileType.CITY)
        self.board_tile = BoardTile.objects.create(
            board=self.board,
            tile=self.tile,
            position=5
        )
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.game = Game.objects.create(board=self.board, owner=self.user)
        self.player = Player.objects.create(display_name="Test Player")
        self.tile_state = GameBoardTileState.objects.create(
            game=self.game,
            board_tile=self.board_tile,
            position=5
        )
        self.bid = Bid.objects.create(
            game=self.game,
            player=self.player,
            board_tile_state=self.tile_state,
            amount=150
        )

    def test_bid_creation(self):
        """Test Bid is created correctly"""
        self.assertEqual(self.bid.amount, 150)
        self.assertEqual(self.bid.player, self.player)


class ChatMessageModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", size=10)
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.game = Game.objects.create(board=self.board, owner=self.user)
        self.player = Player.objects.create(display_name="Test Player")
        self.message = ChatMessage.objects.create(
            game=self.game,
            player=self.player,
            message="Hello, world!",
            is_system=False
        )

    def test_chat_message_creation(self):
        """Test ChatMessage is created correctly"""
        self.assertEqual(self.message.message, "Hello, world!")
        self.assertFalse(self.message.is_system)

    def test_system_message(self):
        """Test creating a system message"""
        sys_msg = ChatMessage.objects.create(
            game=self.game,
            message="Game started!",
            is_system=True
        )
        self.assertTrue(sys_msg.is_system)
        self.assertIsNone(sys_msg.player)


class GameFlowTest(TestCase):
    """Test complete game flow"""
    
    def setUp(self):
        # Create board with tiles
        self.board = Board.objects.create(name="Test Board", size=10)
        
        # Create some tiles
        for i in range(10):
            tile = Tile.objects.create(
                title=f"Tile {i}",
                tile_type=TileType.CITY if i > 0 else TileType.START
            )
            BoardTile.objects.create(
                board=self.board,
                tile=tile,
                position=i
            )
        
        # Create users and players
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")
        
        self.player1 = Player.objects.create(user=self.user1, display_name="Player 1")
        self.player2 = Player.objects.create(user=self.user2, display_name="Player 2")
        
        # Create game
        self.game = Game.objects.create(
            board=self.board,
            owner=self.user1,
            name="Test Game",
            max_players=4
        )

    def test_game_setup_flow(self):
        """Test setting up a game with players"""
        # Add players to lobby
        lobby_player1 = LobbyPlayer.objects.create(
            game=self.game,
            player=self.player1,
            seat_index=0,
            is_owner=True,
            is_ready=False
        )
        lobby_player2 = LobbyPlayer.objects.create(
            game=self.game,
            player=self.player2,
            seat_index=1,
            is_ready=False
        )
        
        # Check game cannot start yet
        self.assertFalse(self.game.can_start(self.user1))
        
        # Mark players as ready
        lobby_player1.is_ready = True
        lobby_player1.save()
        lobby_player2.is_ready = True
        lobby_player2.save()
        
        # Now game can start
        self.assertTrue(self.game.can_start(self.user1))
        
        # Start the game
        self.game.start(self.user1)
        
        # Check game state after start
        self.assertEqual(self.game.status, GameStatus.ACTIVE)
        self.assertIsNotNone(self.game.started_at)
        
        # Check that tile states were created
        tile_states = GameBoardTileState.objects.filter(game=self.game)
        self.assertEqual(tile_states.count(), 10)
        
        # Check that first turn was created
        turn = Turn.objects.filter(game=self.game).first()
        self.assertIsNotNone(turn)
        self.assertEqual(turn.round_number, 1)

    def test_game_cannot_start_without_enough_players(self):
        """Test that game cannot start with only one player"""
        LobbyPlayer.objects.create(
            game=self.game,
            player=self.player1,
            seat_index=0,
            is_owner=True,
            is_ready=True
        )
        
        self.assertFalse(self.game.can_start(self.user1))

    def test_non_owner_cannot_start_game(self):
        """Test that non-owner cannot start game"""
        LobbyPlayer.objects.create(
            game=self.game,
            player=self.player1,
            seat_index=0,
            is_owner=True,
            is_ready=True
        )
        LobbyPlayer.objects.create(
            game=self.game,
            player=self.player2,
            seat_index=1,
            is_ready=True
        )
        
        # user2 is not the owner
        self.assertFalse(self.game.can_start(self.user2))

    def test_initialize_board_state(self):
        """Test that initialize_board_state creates correct states"""
        self.game.initialize_board_state()
        
        states = GameBoardTileState.objects.filter(game=self.game)
        self.assertEqual(states.count(), 10)
        
        # Check positions are correct
        positions = set(state.position for state in states)
        self.assertEqual(positions, set(range(10)))
        
        # Check no double initialization
        initial_count = states.count()
        self.game.initialize_board_state()
        self.assertEqual(GameBoardTileState.objects.filter(game=self.game).count(), initial_count)
