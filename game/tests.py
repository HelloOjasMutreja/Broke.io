from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import (
    Board, Tile, BoardTile, BoardPosition, City, Game, Player, LobbyPlayer,
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
            tile_type=TileType.CUSTOM,  # Changed from CITY
            description="A property tile",
            action={"type": "property", "buyable": True},
            metadata={"color": "brown"}
        )

    def test_tile_creation(self):
        """Test tile is created correctly"""
        self.assertEqual(self.tile.title, "Mediterranean Avenue")
        self.assertEqual(self.tile.tile_type, TileType.CUSTOM)  # Changed from CITY
        self.assertTrue(self.tile.action["buyable"])

    def test_tile_str(self):
        """Test tile string representation"""
        self.assertEqual(str(self.tile), "Mediterranean Avenue [CUSTOM]")  # Changed from CITY


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
            tile_type=TileType.CUSTOM  # Changed from CITY
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
        self.tile = Tile.objects.create(title="Property", tile_type=TileType.CUSTOM)  # Changed from CITY
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
        self.tile = Tile.objects.create(title="Property", tile_type=TileType.CUSTOM)  # Changed from CITY
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
                tile_type=TileType.CUSTOM if i > 0 else TileType.START  # Changed CITY to CUSTOM
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


class BoardPositionModelTest(TestCase):
    """Test the new BoardPosition model"""
    
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", size=10)
        self.tile = Tile.objects.create(title="GO", tile_type=TileType.START)
        self.city_tile = Tile.objects.create(title="Park Place", tile_type=TileType.CUSTOM)
        self.city = City.objects.create(
            tile=self.city_tile,
            base_price=350,
            rent_base=35
        )

    def test_board_position_with_tile(self):
        """Test creating BoardPosition with a tile"""
        bp = BoardPosition.objects.create(
            board=self.board,
            position=0,
            tile=self.tile
        )
        self.assertEqual(bp.position, 0)
        self.assertEqual(bp.tile, self.tile)
        self.assertIsNone(bp.city)

    def test_board_position_with_city(self):
        """Test creating BoardPosition with a city"""
        bp = BoardPosition.objects.create(
            board=self.board,
            position=1,
            city=self.city
        )
        self.assertEqual(bp.position, 1)
        self.assertIsNone(bp.tile)
        self.assertEqual(bp.city, self.city)

    def test_board_position_validation_both_set(self):
        """Test that BoardPosition cannot have both tile and city"""
        with self.assertRaises(ValidationError):
            bp = BoardPosition(
                board=self.board,
                position=2,
                tile=self.tile,
                city=self.city
            )
            bp.save()

    def test_board_position_validation_neither_set(self):
        """Test that BoardPosition must have either tile or city"""
        with self.assertRaises(ValidationError):
            bp = BoardPosition(
                board=self.board,
                position=2
            )
            bp.save()

    def test_board_position_unique_constraint(self):
        """Test that same position cannot be used twice on same board"""
        BoardPosition.objects.create(
            board=self.board,
            position=0,
            tile=self.tile
        )
        with self.assertRaises(Exception):
            BoardPosition.objects.create(
                board=self.board,
                position=0,
                city=self.city
            )

    def test_board_position_str(self):
        """Test BoardPosition string representation"""
        bp = BoardPosition.objects.create(
            board=self.board,
            position=0,
            tile=self.tile
        )
        self.assertIn("Test Board", str(bp))
        self.assertIn("GO", str(bp))
        self.assertIn("0", str(bp))


class BoardInitializationTest(TestCase):
    """Test board auto-initialization functionality"""
    
    def test_board_auto_initializes_on_creation(self):
        """Test that board positions are auto-created when board is created"""
        board = Board.objects.create(name="Auto Board", size=5)
        
        # Manually call initialize_positions since signal uses on_commit
        # which doesn't fire in test transactions
        board.initialize_positions()
        
        # Check that special positions were created
        special_pos = board.default_special_positions()
        
        # Check special positions exist
        for name, pos in special_pos.items():
            bp = BoardPosition.objects.filter(board=board, position=pos).first()
            self.assertIsNotNone(
                bp, 
                f"Special position {name} at {pos} should be auto-created"
            )
            self.assertIsNotNone(bp.tile, f"Special position {name} should have a tile")

    def test_initialize_positions_idempotent(self):
        """Test that initialize_positions can be called multiple times safely"""
        board = Board.objects.create(name="Test Board", size=5)
        
        # Call initialize_positions multiple times
        board.initialize_positions()
        board.initialize_positions()
        board.initialize_positions()
        
        # Check that we don't have duplicate positions
        positions = BoardPosition.objects.filter(board=board)
        position_values = [p.position for p in positions]
        
        # No duplicates
        self.assertEqual(len(position_values), len(set(position_values)))

    def test_initialize_positions_special_tiles(self):
        """Test that special positions get correct tile types"""
        board = Board.objects.create(name="Test Board", size=5)
        board.initialize_positions()
        
        special_pos = board.default_special_positions()
        
        # Check START tile
        start_bp = BoardPosition.objects.get(board=board, position=special_pos["start"])
        self.assertEqual(start_bp.tile.tile_type, TileType.START)
        
        # Check JAIL tile
        prison_bp = BoardPosition.objects.get(board=board, position=special_pos["prison"])
        self.assertEqual(prison_bp.tile.tile_type, TileType.JAIL)
        
        # Check VACATION tile
        vacation_bp = BoardPosition.objects.get(board=board, position=special_pos["vacation"])
        self.assertEqual(vacation_bp.tile.tile_type, TileType.VACATION)
        
        # Check GO_TO_JAIL tile
        go_to_prison_bp = BoardPosition.objects.get(board=board, position=special_pos["go_to_prison"])
        self.assertEqual(go_to_prison_bp.tile.tile_type, TileType.GO_TO_JAIL)

    def test_initialize_positions_does_not_overwrite_custom(self):
        """Test that initialize_positions doesn't overwrite existing positions"""
        board = Board.objects.create(name="Test Board", size=5)
        
        # Create a custom tile at position 0 (which would normally be START)
        custom_tile = Tile.objects.create(title="Custom", tile_type=TileType.CUSTOM)
        custom_bp = BoardPosition.objects.create(
            board=board,
            position=0,
            tile=custom_tile
        )
        
        # Now initialize positions
        board.initialize_positions()
        
        # Check that position 0 still has the custom tile
        bp = BoardPosition.objects.get(board=board, position=0)
        self.assertEqual(bp.tile.title, "Custom")
        self.assertEqual(bp.tile.tile_type, TileType.CUSTOM)


class TileTypeTest(TestCase):
    """Test that TileType.CITY has been removed"""
    
    def test_city_not_in_tile_type(self):
        """Test that CITY is no longer a valid TileType"""
        tile_types = [choice[0] for choice in TileType.choices]
        self.assertNotIn("CITY", tile_types)
    
    def test_vacation_in_tile_type(self):
        """Test that VACATION was added to TileType"""
        tile_types = [choice[0] for choice in TileType.choices]
        self.assertIn("VACATION", tile_types)


class GameBoardTileStateNewSchemaTest(TestCase):
    """Test GameBoardTileState works with new BoardPosition schema"""
    
    def setUp(self):
        self.board = Board.objects.create(name="Test Board", size=5)
        self.tile = Tile.objects.create(title="Property", tile_type=TileType.CUSTOM)
        self.board_position = BoardPosition.objects.create(
            board=self.board,
            position=5,
            tile=self.tile
        )
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.game = Game.objects.create(board=self.board, owner=self.user)
        self.player = Player.objects.create(display_name="Test Player")

    def test_tile_state_with_board_position(self):
        """Test creating GameBoardTileState with BoardPosition"""
        tile_state = GameBoardTileState.objects.create(
            game=self.game,
            board_position=self.board_position,
            position=5,
            owner=self.player,
            houses=2
        )
        self.assertEqual(tile_state.board_position, self.board_position)
        self.assertIsNone(tile_state.board_tile)
        self.assertEqual(tile_state.houses, 2)

    def test_initialize_board_state_with_positions(self):
        """Test that initialize_board_state works with BoardPosition"""
        # Note: setUp already creates a position at 5
        # Create some more board positions (within valid range for size 5)
        # size 5 means positions 0-24 are valid
        for i in range(5):
            tile = Tile.objects.create(title=f"Tile {i}", tile_type=TileType.CUSTOM)
            BoardPosition.objects.create(board=self.board, position=i, tile=tile)
        
        # Initialize game board state
        self.game.initialize_board_state()
        
        # Check that states were created with board_position references
        # We expect 6 states: 5 from the loop above + 1 from setUp (position 5)
        states = GameBoardTileState.objects.filter(game=self.game)
        self.assertEqual(states.count(), 6)
        
        for state in states:
            self.assertIsNotNone(state.board_position)
            self.assertIsNone(state.board_tile)  # Should not use legacy field


class GameModeAndJoinTest(TestCase):
    """Test game mode filtering and join functionality"""
    
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.user3 = User.objects.create_user(username='user3', password='pass123')
        
        # Create board
        self.board = Board.objects.create(name="Test Board", size=10)
        self.board.initialize_positions()
        
        # Import GameMode here to avoid issues if it wasn't imported at top
        from .models import GameMode
        self.GameMode = GameMode
        
    def test_game_mode_default(self):
        """Test that game mode defaults to ONLINE"""
        game = Game.objects.create(
            name="Default Game",
            owner=self.user1,
            board=self.board
        )
        self.assertEqual(game.mode, self.GameMode.ONLINE)
    
    def test_game_mode_choices(self):
        """Test all game mode choices can be set"""
        for mode in [self.GameMode.SOLO, self.GameMode.FRIENDS, self.GameMode.ONLINE]:
            game = Game.objects.create(
                name=f"Game {mode}",
                owner=self.user1,
                board=self.board,
                mode=mode
            )
            self.assertEqual(game.mode, mode)
    
    def test_get_active_players_count(self):
        """Test get_active_players_count method"""
        game = Game.objects.create(
            name="Test Game",
            owner=self.user1,
            board=self.board
        )
        
        # Initially no players
        self.assertEqual(game.get_active_players_count(), 0)
        
        # Add a player
        player1 = Player.objects.create(user=self.user1, display_name='Player1')
        LobbyPlayer.objects.create(game=game, player=player1, seat_index=0)
        self.assertEqual(game.get_active_players_count(), 1)
        
        # Add another player
        player2 = Player.objects.create(user=self.user2, display_name='Player2')
        LobbyPlayer.objects.create(game=game, player=player2, seat_index=1)
        self.assertEqual(game.get_active_players_count(), 2)
    
    def test_is_full(self):
        """Test is_full method"""
        game = Game.objects.create(
            name="Test Game",
            owner=self.user1,
            board=self.board,
            max_players=2
        )
        
        # Game is not full initially
        self.assertFalse(game.is_full())
        
        # Add one player
        player1 = Player.objects.create(user=self.user1, display_name='Player1')
        LobbyPlayer.objects.create(game=game, player=player1, seat_index=0)
        self.assertFalse(game.is_full())
        
        # Add second player - now full
        player2 = Player.objects.create(user=self.user2, display_name='Player2')
        LobbyPlayer.objects.create(game=game, player=player2, seat_index=1)
        self.assertTrue(game.is_full())
    
    def test_can_user_join_lobby_status(self):
        """Test can_user_join with different game statuses"""
        game = Game.objects.create(
            name="Test Game",
            owner=self.user1,
            board=self.board,
            status=GameStatus.LOBBY
        )
        
        # User can join lobby game
        self.assertTrue(game.can_user_join(self.user2))
        
        # User cannot join active game
        game.status = GameStatus.ACTIVE
        game.save()
        self.assertFalse(game.can_user_join(self.user2))
    
    def test_can_user_join_full_game(self):
        """Test can_user_join when game is full"""
        game = Game.objects.create(
            name="Test Game",
            owner=self.user1,
            board=self.board,
            max_players=1
        )
        
        # Add one player to fill the game
        player1 = Player.objects.create(user=self.user1, display_name='Player1')
        LobbyPlayer.objects.create(game=game, player=player1, seat_index=0)
        
        # User cannot join full game
        self.assertFalse(game.can_user_join(self.user2))
    
    def test_can_user_join_already_in_game(self):
        """Test can_user_join when user is already in game"""
        game = Game.objects.create(
            name="Test Game",
            owner=self.user1,
            board=self.board
        )
        
        # Add user2 to the game
        player2 = Player.objects.create(user=self.user2, display_name='Player2')
        LobbyPlayer.objects.create(game=game, player=player2, seat_index=0)
        
        # User cannot join again
        self.assertFalse(game.can_user_join(self.user2))
    
    def test_can_user_join_unauthenticated(self):
        """Test can_user_join with unauthenticated user"""
        game = Game.objects.create(
            name="Test Game",
            owner=self.user1,
            board=self.board
        )
        
        # None user cannot join
        self.assertFalse(game.can_user_join(None))


class GameLobbyViewTest(TestCase):
    """Test game lobby view filtering"""
    
    def setUp(self):
        from django.test import Client
        from .models import GameMode
        
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        
        # Create board
        self.board = Board.objects.create(name="Test Board", size=10)
        self.board.initialize_positions()
        
        # Create games with different modes
        self.online_game = Game.objects.create(
            name="Online Game",
            owner=self.user,
            board=self.board,
            mode=GameMode.ONLINE,
            status=GameStatus.LOBBY
        )
        
        self.friends_game = Game.objects.create(
            name="Friends Game",
            owner=self.user,
            board=self.board,
            mode=GameMode.FRIENDS,
            status=GameStatus.LOBBY
        )
        
        self.solo_game = Game.objects.create(
            name="Solo Game",
            owner=self.user,
            board=self.board,
            mode=GameMode.SOLO,
            status=GameStatus.LOBBY
        )
        
        self.active_game = Game.objects.create(
            name="Active Online Game",
            owner=self.user,
            board=self.board,
            mode=GameMode.ONLINE,
            status=GameStatus.ACTIVE
        )
    
    def test_lobby_shows_only_online_lobby_games(self):
        """Test that lobby view only shows ONLINE games in LOBBY status"""
        response = self.client.get('/game/')
        self.assertEqual(response.status_code, 200)
        
        # Check that only online lobby game appears
        games = response.context['games']
        self.assertEqual(games.count(), 1)
        self.assertEqual(games[0].name, "Online Game")
    
    def test_lobby_hides_friends_games(self):
        """Test that FRIENDS games don't appear in public lobby"""
        response = self.client.get('/game/')
        content = response.content.decode('utf-8')
        
        # Online game should be visible
        self.assertIn("Online Game", content)
        
        # Friends game should NOT be visible
        self.assertNotIn("Friends Game", content)
    
    def test_join_button_appears_for_authenticated_user(self):
        """Test that Join Game button appears for logged-in users"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get('/game/')
        content = response.content.decode('utf-8')
        
        # Join Game button should appear
        self.assertIn("Join Game", content)


class JoinGameViewTest(TestCase):
    """Test join game functionality"""
    
    def setUp(self):
        from django.test import Client
        
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        
        # Create board
        self.board = Board.objects.create(name="Test Board", size=10)
        self.board.initialize_positions()
        
        # Create game
        self.game = Game.objects.create(
            name="Test Game",
            owner=self.user1,
            board=self.board,
            status=GameStatus.LOBBY
        )
        
        # Add owner to game
        player1 = Player.objects.create(user=self.user1, display_name='User1')
        LobbyPlayer.objects.create(game=self.game, player=player1, seat_index=0, is_owner=True)
    
    def test_join_game_success(self):
        """Test successful game join"""
        self.client.login(username='user2', password='pass123')
        
        # Count players before join
        initial_count = self.game.get_active_players_count()
        
        # Join game
        response = self.client.get(f'/game/{self.game.id}/join/', follow=True)
        
        # Should redirect to game detail
        self.assertEqual(response.status_code, 200)
        
        # Check player was added
        self.game.refresh_from_db()
        self.assertEqual(self.game.get_active_players_count(), initial_count + 1)
    
    def test_join_game_requires_login(self):
        """Test that joining requires authentication"""
        response = self.client.get(f'/game/{self.game.id}/join/')
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)
