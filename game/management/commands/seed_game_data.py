"""
Management command to seed the database with test data for the game.

This creates boards, tiles, games, players, and other game entities
to enable full game testing without manual data entry.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from game.models import (
    Board, Tile, BoardTile, City, Game, Player, LobbyPlayer,
    GameBoardTileState, Turn, ActionLog, Trade, Bid, ChatMessage,
    GameStatus, TileType
)
import random


class Command(BaseCommand):
    help = 'Seeds the database with test data for game testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing game data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing game data...'))
            self._clear_data()

        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        with transaction.atomic():
            # Create users
            users = self._create_users()
            self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))

            # Create boards with tiles
            boards = self._create_boards()
            self.stdout.write(self.style.SUCCESS(f'Created {len(boards)} boards'))

            # Create games in various states
            games = self._create_games(boards, users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(games)} games'))

            self.stdout.write(self.style.SUCCESS('\n=== Seed data created successfully! ==='))
            self.stdout.write(self.style.SUCCESS('\nTest Credentials:'))
            self.stdout.write('  Username: player1 | Password: testpass123')
            self.stdout.write('  Username: player2 | Password: testpass123')
            self.stdout.write('  Username: player3 | Password: testpass123')
            self.stdout.write('  Username: player4 | Password: testpass123')
            self.stdout.write('\nGames Created:')
            for game in games:
                player_count = game.lobby_players.count()
                self.stdout.write(f'  - {game.name} ({game.status}): {player_count} players')

    def _clear_data(self):
        """Clear existing game data."""
        ChatMessage.objects.all().delete()
        Bid.objects.all().delete()
        Trade.objects.all().delete()
        ActionLog.objects.all().delete()
        Turn.objects.all().delete()
        GameBoardTileState.objects.all().delete()
        LobbyPlayer.objects.all().delete()
        Player.objects.all().delete()
        Game.objects.all().delete()
        City.objects.all().delete()
        BoardTile.objects.all().delete()
        Tile.objects.all().delete()
        Board.objects.all().delete()

    def _create_users(self):
        """Create test users."""
        users = []
        for i in range(1, 5):
            username = f'player{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': f'Player{i}',
                    'last_name': 'Test'
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            users.append(user)
        return users

    def _create_boards(self):
        """Create game boards with tiles."""
        boards = []

        # Classic Monopoly-style board (10x10 = 100 tiles, but we'll use 40 positions)
        board = Board.objects.create(
            name="Classic Board",
            size=10,
            theme="classic",
            description="Traditional Monopoly-style board with 40 spaces"
        )
        self._create_classic_tiles(board)
        boards.append(board)

        # Cyber City board
        board = Board.objects.create(
            name="Cyber City",
            size=10,
            theme="cyber",
            description="Futuristic neon-themed board"
        )
        self._create_themed_tiles(board, "Cyber")
        boards.append(board)

        return boards

    def _create_classic_tiles(self, board):
        """Create classic Monopoly-style tiles."""
        # Property data
        properties = [
            {'name': 'Mediterranean Avenue', 'price': 60, 'rent': 2, 'color': 'brown'},
            {'name': 'Baltic Avenue', 'price': 60, 'rent': 4, 'color': 'brown'},
            {'name': 'Oriental Avenue', 'price': 100, 'rent': 6, 'color': 'lightblue'},
            {'name': 'Vermont Avenue', 'price': 100, 'rent': 6, 'color': 'lightblue'},
            {'name': 'Connecticut Avenue', 'price': 120, 'rent': 8, 'color': 'lightblue'},
            {'name': 'St. Charles Place', 'price': 140, 'rent': 10, 'color': 'pink'},
            {'name': 'States Avenue', 'price': 140, 'rent': 10, 'color': 'pink'},
            {'name': 'Virginia Avenue', 'price': 160, 'rent': 12, 'color': 'pink'},
            {'name': 'St. James Place', 'price': 180, 'rent': 14, 'color': 'orange'},
            {'name': 'Tennessee Avenue', 'price': 180, 'rent': 14, 'color': 'orange'},
            {'name': 'New York Avenue', 'price': 200, 'rent': 16, 'color': 'orange'},
            {'name': 'Kentucky Avenue', 'price': 220, 'rent': 18, 'color': 'red'},
            {'name': 'Indiana Avenue', 'price': 220, 'rent': 18, 'color': 'red'},
            {'name': 'Illinois Avenue', 'price': 240, 'rent': 20, 'color': 'red'},
            {'name': 'Atlantic Avenue', 'price': 260, 'rent': 22, 'color': 'yellow'},
            {'name': 'Ventnor Avenue', 'price': 260, 'rent': 22, 'color': 'yellow'},
            {'name': 'Marvin Gardens', 'price': 280, 'rent': 24, 'color': 'yellow'},
            {'name': 'Pacific Avenue', 'price': 300, 'rent': 26, 'color': 'green'},
            {'name': 'North Carolina Avenue', 'price': 300, 'rent': 26, 'color': 'green'},
            {'name': 'Pennsylvania Avenue', 'price': 320, 'rent': 28, 'color': 'green'},
            {'name': 'Park Place', 'price': 350, 'rent': 35, 'color': 'darkblue'},
            {'name': 'Boardwalk', 'price': 400, 'rent': 50, 'color': 'darkblue'},
        ]

        # Special tiles
        special_tiles = [
            (0, 'GO', TileType.START),
            (5, 'Reading Railroad', TileType.UTILITY),
            (10, 'Jail / Just Visiting', TileType.JAIL),
            (15, 'Pennsylvania Railroad', TileType.UTILITY),
            (20, 'Free Parking', TileType.FREE_PARKING),
            (25, 'B&O Railroad', TileType.UTILITY),
            (30, 'Go to Jail', TileType.GO_TO_JAIL),
            (35, 'Short Line Railroad', TileType.UTILITY),
        ]

        # Create tiles and board tiles
        prop_index = 0
        for pos in range(40):
            # Check if it's a special tile
            is_special = False
            for special_pos, special_name, special_type in special_tiles:
                if pos == special_pos:
                    tile = Tile.objects.create(
                        title=special_name,
                        tile_type=special_type,
                        description=f"Special tile: {special_name}"
                    )
                    BoardTile.objects.create(board=board, tile=tile, position=pos)
                    is_special = True
                    break
            
            # If not special and we have properties left, make it a property
            if not is_special and prop_index < len(properties):
                prop = properties[prop_index]
                tile = Tile.objects.create(
                    title=prop['name'],
                    tile_type=TileType.CITY,
                    description=f"Property in {prop['color']} group"
                )
                # Create city data
                City.objects.create(
                    tile=tile,
                    base_price=prop['price'],
                    mortgage_value=prop['price'] // 2,
                    rent_base=prop['rent'],
                    rent_house_1=prop['rent'] * 5,
                    rent_house_2=prop['rent'] * 15,
                    rent_house_3=prop['rent'] * 45,
                    rent_house_4=prop['rent'] * 60,
                    rent_hotel=prop['rent'] * 75,
                    house_cost=prop['price'] // 2,
                    hotel_cost=prop['price'] // 2,
                    color_group=prop['color']
                )
                BoardTile.objects.create(board=board, tile=tile, position=pos)
                prop_index += 1
            elif not is_special:
                # Fill remaining with chance/treasure
                tile_type = TileType.CHANCE if pos % 2 == 0 else TileType.TREASURE
                tile = Tile.objects.create(
                    title=f"{tile_type} Card",
                    tile_type=tile_type,
                    description="Draw a card"
                )
                BoardTile.objects.create(board=board, tile=tile, position=pos)

    def _create_themed_tiles(self, board, theme_prefix):
        """Create themed tiles for non-classic boards."""
        for i in range(40):
            if i == 0:
                tile_type = TileType.START
                name = 'START'
            elif i == 10:
                tile_type = TileType.JAIL
                name = 'Holding Cell'
            elif i == 20:
                tile_type = TileType.FREE_PARKING
                name = 'Safe Zone'
            elif i == 30:
                tile_type = TileType.GO_TO_JAIL
                name = 'Capture'
            elif i % 7 == 0:
                tile_type = TileType.CHANCE
                name = 'Mystery'
            elif i % 5 == 0:
                tile_type = TileType.UTILITY
                name = f'{theme_prefix} Station {i // 5}'
            else:
                tile_type = TileType.CITY
                name = f'{theme_prefix} Space {i+1}'

            tile = Tile.objects.create(
                title=name,
                tile_type=tile_type,
                description=f"{theme_prefix} themed tile"
            )

            # Add city data for city tiles
            if tile_type == TileType.CITY:
                price = (i + 1) * 20
                City.objects.create(
                    tile=tile,
                    base_price=price,
                    mortgage_value=price // 2,
                    rent_base=price // 10,
                    rent_house_1=price // 2,
                    rent_house_2=price,
                    rent_house_3=price * 2,
                    rent_house_4=price * 3,
                    rent_hotel=price * 4,
                    house_cost=price // 4,
                    hotel_cost=price // 4,
                    color_group=f"Group {i // 5}"
                )

            BoardTile.objects.create(board=board, tile=tile, position=i)

    def _create_games(self, boards, users):
        """Create games in various states."""
        games = []

        # Game 1: Waiting for players
        game = Game.objects.create(
            board=boards[0],
            owner=users[0],
            name="Waiting Room Game",
            status=GameStatus.LOBBY,
            max_players=4
        )
        player = Player.objects.create(
            user=users[0],
            display_name=users[0].username,
            is_ai=False
        )
        LobbyPlayer.objects.create(
            game=game,
            player=player,
            seat_index=0,
            cash=1500,
            is_ready=False,
            is_owner=True
        )
        games.append(game)

        # Game 2: Full game ready to start
        game = Game.objects.create(
            board=boards[0],
            owner=users[0],
            name="Full House - Ready to Start",
            status=GameStatus.LOBBY,
            max_players=4
        )
        for i, user in enumerate(users):
            player = Player.objects.create(
                user=user,
                display_name=user.username,
                is_ai=False
            )
            LobbyPlayer.objects.create(
                game=game,
                player=player,
                seat_index=i,
                cash=1500,
                is_ready=(i > 0),  # All except owner are ready
                is_owner=(i == 0)
            )
        games.append(game)

        # Game 3: Active game in progress
        game = self._create_active_game(boards[0], users[:3])
        games.append(game)

        return games

    def _create_active_game(self, board, users):
        """Create an active game with turns and actions."""
        game = Game.objects.create(
            board=board,
            owner=users[0],
            name="Active Game - In Progress",
            status=GameStatus.ACTIVE,
            max_players=4
        )

        # Create players
        players = []
        for i, user in enumerate(users):
            player = Player.objects.create(
                user=user,
                display_name=user.username,
                is_ai=False
            )
            LobbyPlayer.objects.create(
                game=game,
                player=player,
                seat_index=i,
                cash=1500 + random.randint(-300, 300),
                position=random.randint(0, 39),
                is_ready=True,
                is_owner=(i == 0)
            )
            players.append(player)

        # Initialize board state
        game.initialize_board_state()

        # Set some tile ownership
        tile_states = list(GameBoardTileState.objects.filter(game=game))
        for i, state in enumerate(tile_states[:10]):
            state.owner = players[i % len(players)]
            state.houses = random.randint(0, 2)
            state.save()

        # Create current turn
        Turn.objects.create(
            game=game,
            current_player=players[0],
            round_number=2
        )

        # Add some action logs
        for player in players:
            ActionLog.objects.create(
                game=game,
                player=player,
                action_type="roll_dice",
                payload={"dice1": random.randint(1, 6), "dice2": random.randint(1, 6)}
            )

        # Add some chat messages
        messages = [
            "Let's play!",
            "Good luck everyone!",
            "Nice move!",
        ]
        for i, msg in enumerate(messages):
            ChatMessage.objects.create(
                game=game,
                player=players[i % len(players)],
                message=msg,
                is_system=False
            )

        return game
