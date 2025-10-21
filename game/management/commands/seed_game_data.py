"""
Management command to seed the database with test data for the game.

This creates boards, tiles, games, players, cards, and other game entities
to enable full game testing without manual data entry.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from game.models import (
    Board, Game, Player, Tile, City, Resource,
    Turn, Action, Trade, PowerUp, ChatMessage,
    Auction, Bid, Card, Minigame, Transaction
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

            # Create cards
            cards = self._create_cards()
            self.stdout.write(self.style.SUCCESS(f'Created {len(cards)} cards'))

            # Create games in various states
            games = self._create_games(boards, users)
            self.stdout.write(self.style.SUCCESS(f'Created {len(games)} games'))

            # Count cities created
            total_cities = City.objects.count()
            
            self.stdout.write(self.style.SUCCESS('\n=== Seed data created successfully! ==='))
            self.stdout.write(self.style.SUCCESS('\nTest Credentials:'))
            self.stdout.write('  Username: player1 | Password: testpass123')
            self.stdout.write('  Username: player2 | Password: testpass123')
            self.stdout.write('  Username: player3 | Password: testpass123')
            self.stdout.write('  Username: player4 | Password: testpass123')
            self.stdout.write('\nGames Created:')
            for game in games:
                city_count = City.objects.filter(player__game=game).count()
                self.stdout.write(f'  - {game.name} ({game.status}): {game.get_active_players_count()} players, {city_count} cities')
            self.stdout.write(f'\nTotal cities built: {total_cities}')

    def _clear_data(self):
        """Clear existing game data."""
        Card.objects.all().delete()
        Transaction.objects.all().delete()
        Minigame.objects.all().delete()
        Bid.objects.all().delete()
        Auction.objects.all().delete()
        ChatMessage.objects.all().delete()
        PowerUp.objects.all().delete()
        Trade.objects.all().delete()
        Action.objects.all().delete()
        Turn.objects.all().delete()
        Resource.objects.all().delete()
        City.objects.all().delete()
        Tile.objects.all().delete()
        Player.objects.all().delete()
        Game.objects.all().delete()
        Board.objects.all().delete()
        # Optionally clear users (commented out to preserve superuser)
        # User.objects.filter(username__startswith='player').delete()

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

        # Classic Monopoly-style board
        board = Board.objects.create(
            name="Classic Board",
            width=11,
            height=11,
            theme="classic",
            description="Traditional Monopoly-style board with 40 spaces",
            is_active=True
        )
        self._create_classic_tiles(board)
        boards.append(board)

        # Cyber City board
        board = Board.objects.create(
            name="Cyber City",
            width=11,
            height=11,
            theme="cyber",
            description="Futuristic neon-themed board",
            is_active=True
        )
        self._create_themed_tiles(board, "Cyber")
        boards.append(board)

        # Fantasy board
        board = Board.objects.create(
            name="Fantasy Realm",
            width=11,
            height=11,
            theme="fantasy",
            description="Magical fantasy-themed board",
            is_active=True
        )
        self._create_themed_tiles(board, "Fantasy")
        boards.append(board)

        return boards

    def _create_classic_tiles(self, board):
        """Create classic Monopoly-style tiles."""
        # Property groups with names, colors, and pricing
        property_groups = [
            # Brown
            {'color': 'brown', 'properties': [
                {'name': 'Mediterranean Avenue', 'price': 60, 'rent': 2},
                {'name': 'Baltic Avenue', 'price': 60, 'rent': 4},
            ]},
            # Light Blue
            {'color': 'lightblue', 'properties': [
                {'name': 'Oriental Avenue', 'price': 100, 'rent': 6},
                {'name': 'Vermont Avenue', 'price': 100, 'rent': 6},
                {'name': 'Connecticut Avenue', 'price': 120, 'rent': 8},
            ]},
            # Pink
            {'color': 'pink', 'properties': [
                {'name': 'St. Charles Place', 'price': 140, 'rent': 10},
                {'name': 'States Avenue', 'price': 140, 'rent': 10},
                {'name': 'Virginia Avenue', 'price': 160, 'rent': 12},
            ]},
            # Orange
            {'color': 'orange', 'properties': [
                {'name': 'St. James Place', 'price': 180, 'rent': 14},
                {'name': 'Tennessee Avenue', 'price': 180, 'rent': 14},
                {'name': 'New York Avenue', 'price': 200, 'rent': 16},
            ]},
            # Red
            {'color': 'red', 'properties': [
                {'name': 'Kentucky Avenue', 'price': 220, 'rent': 18},
                {'name': 'Indiana Avenue', 'price': 220, 'rent': 18},
                {'name': 'Illinois Avenue', 'price': 240, 'rent': 20},
            ]},
            # Yellow
            {'color': 'yellow', 'properties': [
                {'name': 'Atlantic Avenue', 'price': 260, 'rent': 22},
                {'name': 'Ventnor Avenue', 'price': 260, 'rent': 22},
                {'name': 'Marvin Gardens', 'price': 280, 'rent': 24},
            ]},
            # Green
            {'color': 'green', 'properties': [
                {'name': 'Pacific Avenue', 'price': 300, 'rent': 26},
                {'name': 'North Carolina Avenue', 'price': 300, 'rent': 26},
                {'name': 'Pennsylvania Avenue', 'price': 320, 'rent': 28},
            ]},
            # Dark Blue
            {'color': 'darkblue', 'properties': [
                {'name': 'Park Place', 'price': 350, 'rent': 35},
                {'name': 'Boardwalk', 'price': 400, 'rent': 50},
            ]},
        ]

        # Special spaces
        special_tiles = [
            {'position': 0, 'name': 'GO', 'terrain': 'go'},
            {'position': 2, 'name': 'Community Chest', 'terrain': 'community_chest'},
            {'position': 4, 'name': 'Income Tax', 'terrain': 'tax'},
            {'position': 5, 'name': 'Reading Railroad', 'terrain': 'railroad', 'price': 200, 'rent': 25},
            {'position': 7, 'name': 'Chance', 'terrain': 'chance'},
            {'position': 10, 'name': 'Jail / Just Visiting', 'terrain': 'jail'},
            {'position': 12, 'name': 'Electric Company', 'terrain': 'utility', 'price': 150, 'rent': 10},
            {'position': 15, 'name': 'Pennsylvania Railroad', 'terrain': 'railroad', 'price': 200, 'rent': 25},
            {'position': 17, 'name': 'Community Chest', 'terrain': 'community_chest'},
            {'position': 20, 'name': 'Free Parking', 'terrain': 'free_parking'},
            {'position': 22, 'name': 'Chance', 'terrain': 'chance'},
            {'position': 25, 'name': 'B&O Railroad', 'terrain': 'railroad', 'price': 200, 'rent': 25},
            {'position': 28, 'name': 'Water Works', 'terrain': 'utility', 'price': 150, 'rent': 10},
            {'position': 30, 'name': 'Go to Jail', 'terrain': 'go_to_jail'},
            {'position': 33, 'name': 'Community Chest', 'terrain': 'community_chest'},
            {'position': 35, 'name': 'Short Line Railroad', 'terrain': 'railroad', 'price': 200, 'rent': 25},
            {'position': 36, 'name': 'Chance', 'terrain': 'chance'},
            {'position': 38, 'name': 'Luxury Tax', 'terrain': 'tax'},
        ]

        tiles = []
        position = 0

        # Create special tiles first
        special_positions = {tile['position']: tile for tile in special_tiles}

        # Create all 40 tiles
        for pos in range(40):
            if pos in special_positions:
                tile_data = special_positions[pos]
                tiles.append(Tile(
                    board=board,
                    position=pos,
                    x_coordinate=self._get_x_coord(pos),
                    y_coordinate=self._get_y_coord(pos),
                    name=tile_data['name'],
                    terrain_type=tile_data['terrain'],
                    price=tile_data.get('price', 0),
                    rent=tile_data.get('rent', 0),
                ))
            else:
                # Fill in property spaces
                property_added = False
                for group in property_groups:
                    for prop in group['properties']:
                        if not property_added:
                            tiles.append(Tile(
                                board=board,
                                position=pos,
                                x_coordinate=self._get_x_coord(pos),
                                y_coordinate=self._get_y_coord(pos),
                                name=prop['name'],
                                terrain_type='property',
                                price=prop['price'],
                                rent=prop['rent'],
                                color_group=group['color'],
                            ))
                            group['properties'].remove(prop)
                            property_added = True
                            break
                    if property_added:
                        break

        Tile.objects.bulk_create(tiles)

    def _create_themed_tiles(self, board, theme_prefix):
        """Create themed tiles for non-classic boards."""
        tiles = []
        for i in range(40):
            terrain_type = 'property'
            name = f'{theme_prefix} Space {i+1}'
            price = (i + 1) * 20
            rent = (i + 1) * 2

            # Add some special tiles
            if i == 0:
                terrain_type = 'go'
                name = 'START'
                price = 0
                rent = 0
            elif i == 10:
                terrain_type = 'jail'
                name = 'Holding Cell'
                price = 0
                rent = 0
            elif i == 20:
                terrain_type = 'free_parking'
                name = 'Safe Zone'
                price = 0
                rent = 0
            elif i == 30:
                terrain_type = 'go_to_jail'
                name = 'Capture'
                price = 0
                rent = 0
            elif i % 7 == 0:
                terrain_type = 'chance'
                name = 'Mystery'
                price = 0
                rent = 0
            elif i % 5 == 0:
                terrain_type = 'railroad'
                name = f'{theme_prefix} Station {i // 5}'
                price = 200
                rent = 25

            tiles.append(Tile(
                board=board,
                position=i,
                x_coordinate=self._get_x_coord(i),
                y_coordinate=self._get_y_coord(i),
                name=name,
                terrain_type=terrain_type,
                price=price,
                rent=rent,
            ))

        Tile.objects.bulk_create(tiles)

    def _get_x_coord(self, position):
        """Get X coordinate for position on board."""
        # Simplified coordinate system for 40-space board
        if position <= 10:
            return 10 - position
        elif position <= 20:
            return 0
        elif position <= 30:
            return position - 20
        else:
            return 10

    def _get_y_coord(self, position):
        """Get Y coordinate for position on board."""
        if position <= 10:
            return 10
        elif position <= 20:
            return 20 - position
        elif position <= 30:
            return 0
        else:
            return position - 30

    def _create_cards(self):
        """Create Chance and Community Chest cards."""
        cards = []

        # Chance cards
        chance_cards = [
            {'title': 'Advance to GO', 'description': 'Collect $200', 'effect': {'action': 'move', 'position': 0, 'money': 200}},
            {'title': 'Bank pays you dividend', 'description': 'Collect $50', 'effect': {'money': 50}},
            {'title': 'Go Back 3 Spaces', 'description': '', 'effect': {'action': 'move', 'relative': -3}},
            {'title': 'Go to Jail', 'description': 'Do not pass GO', 'effect': {'action': 'jail'}},
            {'title': 'Make general repairs', 'description': 'Pay $25 per house, $100 per hotel', 'effect': {'pay_per_house': 25, 'pay_per_hotel': 100}},
            {'title': 'Pay poor tax', 'description': 'Pay $15', 'effect': {'money': -15}},
            {'title': 'Take a trip to Reading Railroad', 'description': '', 'effect': {'action': 'move', 'position': 5}},
            {'title': 'Advance to Boardwalk', 'description': '', 'effect': {'action': 'move', 'position': 39}},
            {'title': 'You have been elected Chairman', 'description': 'Pay each player $50', 'effect': {'pay_all': 50}},
            {'title': 'Building loan matures', 'description': 'Collect $150', 'effect': {'money': 150}},
            {'title': 'Get out of Jail Free', 'description': 'Keep until needed', 'effect': {'get_out_of_jail': True}},
        ]

        # Community Chest cards
        community_cards = [
            {'title': 'Advance to GO', 'description': 'Collect $200', 'effect': {'action': 'move', 'position': 0, 'money': 200}},
            {'title': 'Bank error in your favor', 'description': 'Collect $200', 'effect': {'money': 200}},
            {'title': 'Doctor\'s fees', 'description': 'Pay $50', 'effect': {'money': -50}},
            {'title': 'From sale of stock', 'description': 'Get $50', 'effect': {'money': 50}},
            {'title': 'Get out of Jail Free', 'description': 'Keep until needed', 'effect': {'get_out_of_jail': True}},
            {'title': 'Go to Jail', 'description': 'Do not pass GO', 'effect': {'action': 'jail'}},
            {'title': 'Grand Opera Night', 'description': 'Collect $50 from every player', 'effect': {'collect_all': 50}},
            {'title': 'Holiday Fund matures', 'description': 'Collect $100', 'effect': {'money': 100}},
            {'title': 'Income tax refund', 'description': 'Collect $20', 'effect': {'money': 20}},
            {'title': 'Life insurance matures', 'description': 'Collect $100', 'effect': {'money': 100}},
            {'title': 'Pay hospital fees', 'description': 'Pay $100', 'effect': {'money': -100}},
            {'title': 'Pay school fees', 'description': 'Pay $50', 'effect': {'money': -50}},
            {'title': 'Receive $25 consultancy fee', 'description': '', 'effect': {'money': 25}},
            {'title': 'Street repairs', 'description': 'Pay $40 per house, $115 per hotel', 'effect': {'pay_per_house': 40, 'pay_per_hotel': 115}},
            {'title': 'You have won second prize in beauty contest', 'description': 'Collect $10', 'effect': {'money': 10}},
            {'title': 'You inherit $100', 'description': '', 'effect': {'money': 100}},
        ]

        for i, card_data in enumerate(chance_cards):
            cards.append(Card(
                deck='chance',
                title=card_data['title'],
                description=card_data['description'],
                effect=card_data['effect'],
                is_active=True,
                order=i
            ))

        for i, card_data in enumerate(community_cards):
            cards.append(Card(
                deck='community',
                title=card_data['title'],
                description=card_data['description'],
                effect=card_data['effect'],
                is_active=True,
                order=i
            ))

        Card.objects.bulk_create(cards)
        return cards

    def _create_games(self, boards, users):
        """Create games in various states."""
        games = []

        # Game 1: Waiting for players
        game = Game.objects.create(
            board=boards[0],
            name="Waiting Room Game",
            mode="friends",
            status="waiting",
            max_players=4,
            starting_money=1500,
        )
        Player.objects.create(
            game=game,
            user=users[0],
            name=users[0].username,
            money=1500,
            turn_order=0,
        )
        games.append(game)

        # Game 2: Active game in progress
        game = self._create_active_game(boards[0], users[:3])
        games.append(game)

        # Game 3: Full game ready to start
        game = Game.objects.create(
            board=boards[1],
            name="Full House - Ready to Start",
            mode="friends",
            status="waiting",
            max_players=4,
            starting_money=1500,
        )
        for i, user in enumerate(users):
            Player.objects.create(
                game=game,
                user=user,
                name=user.username,
                money=1500,
                turn_order=i,
                token=['🚗', '🚢', '🎩', '🐕'][i],
            )
        games.append(game)

        # Game 4: Solo game with AI
        game = Game.objects.create(
            board=boards[0],
            name="Solo vs AI",
            mode="solo",
            status="active",
            max_players=2,
            starting_money=1500,
        )
        human_player = Player.objects.create(
            game=game,
            user=users[0],
            name=users[0].username,
            money=1200,
            position=15,
            turn_order=0,
        )
        ai_player = Player.objects.create(
            game=game,
            user=None,
            name="AI Bot",
            money=1400,
            position=8,
            turn_order=1,
            is_human=False,
        )
        # Add some owned properties for the solo game
        tiles = game.board.tiles.filter(terrain_type='property')[:5]
        for i, tile in enumerate(tiles):
            if i < 3:
                tile.owner = human_player
            else:
                tile.owner = ai_player
            tile.save()

        # Add cities for solo game
        City.objects.create(
            tile=tiles[0],
            player=human_player,
            name="Capital City",
            level=2,
            population=250,
            defense=20,
            production_capacity=30,
            storage_capacity=300,
            health=100,
            is_capital=True,
        )
        City.objects.create(
            tile=tiles[3],
            player=ai_player,
            name="AI Fortress",
            level=1,
            population=150,
            defense=15,
            production_capacity=20,
            storage_capacity=200,
            health=100,
            is_capital=True,
        )

        games.append(game)

        return games

    def _create_active_game(self, board, users):
        """Create an active game with turns, actions, and owned properties."""
        game = Game.objects.create(
            board=board,
            name="Active Game - Mid Battle",
            mode="friends",
            status="active",
            max_players=4,
            starting_money=1500,
        )

        # Create players with varied stats
        players = []
        player_configs = [
            {'money': 1800, 'position': 12, 'level': 2, 'experience': 120, 'score': 500, 'token': '🚗'},
            {'money': 1200, 'position': 25, 'level': 1, 'experience': 80, 'score': 350, 'token': '🚢'},
            {'money': 1500, 'position': 5, 'level': 1, 'experience': 50, 'score': 200, 'token': '🎩'},
        ]

        for i, (user, config) in enumerate(zip(users, player_configs)):
            player = Player.objects.create(
                game=game,
                user=user,
                name=user.username,
                money=config['money'],
                position=config['position'],
                turn_order=i,
                level=config['level'],
                experience=config['experience'],
                score=config['score'],
                token=config['token'],
            )
            players.append(player)

        # Distribute some properties among players
        properties = list(game.board.tiles.filter(terrain_type='property'))
        for i, tile in enumerate(properties[:15]):
            tile.owner = players[i % len(players)]
            if i < 5:
                tile.improvement_level = random.randint(0, 2)
            tile.save()

        # Create cities on some owned properties
        city_names = [
            "New York", "London", "Tokyo", "Paris", "Berlin",
            "Moscow", "Sydney", "Toronto", "Mumbai", "Dubai"
        ]
        cities_created = []
        for i, tile in enumerate(properties[:10]):
            if tile.owner:
                city = City.objects.create(
                    tile=tile,
                    player=tile.owner,
                    name=city_names[i],
                    level=random.randint(1, 3),
                    population=random.randint(100, 500),
                    defense=random.randint(10, 30),
                    production_capacity=random.randint(10, 50),
                    storage_capacity=random.randint(100, 500),
                    health=random.randint(80, 100),
                    is_capital=(i % len(players) == 0 and i < len(players)),
                )
                cities_created.append(city)

        # Create some turns and actions
        for turn_num in range(1, 8):
            player = players[(turn_num - 1) % len(players)]
            turn = Turn.objects.create(
                game=game,
                player=player,
                turn_number=turn_num,
                round_number=(turn_num - 1) // len(players) + 1,
                phase='end',
                dice_roll={'dice1': random.randint(1, 6), 'dice2': random.randint(1, 6)},
                is_complete=True,
            )

            # Add some actions for this turn
            Action.objects.create(
                turn=turn,
                player=player,
                action_type='roll_dice',
                data={'dice': [turn.dice_roll['dice1'], turn.dice_roll['dice2']]},
            )
            Action.objects.create(
                turn=turn,
                player=player,
                action_type='move',
                data={'from': player.position - turn.dice_roll['dice1'] - turn.dice_roll['dice2'], 'to': player.position},
            )

        # Create current turn
        current_player = players[len(list(Turn.objects.filter(game=game))) % len(players)]
        Turn.objects.create(
            game=game,
            player=current_player,
            turn_number=8,
            round_number=3,
            phase='roll',
            is_complete=False,
        )

        # Add some powerups
        PowerUp.objects.create(
            player=players[0],
            powerup_type='double_rent',
            name='Double Rent',
            description='Doubles rent collected for 2 turns',
            duration=2,
        )
        PowerUp.objects.create(
            player=players[1],
            powerup_type='immunity',
            name='Rent Shield',
            description='Protected from rent for 3 turns',
            duration=3,
        )

        # Add some resources
        for player in players:
            Resource.objects.create(
                player=player,
                resource_type='gold',
                amount=random.randint(50, 200),
                capacity=1000,
                production_rate=10,
            )

        # Add some chat messages
        messages = [
            "Let's play!",
            "Good luck everyone!",
            "Nice move!",
            "I'm coming for your properties 😄",
        ]
        for i, msg in enumerate(messages):
            ChatMessage.objects.create(
                game=game,
                player=players[i % len(players)],
                message_type='player',
                content=msg,
            )

        # Add a completed minigame
        Minigame.objects.create(
            game=game,
            player=players[0],
            minigame_type='quick_math',
            score=85,
            reward=100,
            is_completed=True,
        )

        # Add a transaction
        Transaction.objects.create(
            game=game,
            from_player=players[1],
            to_player=players[0],
            kind='money',
            amount=50,
            reason='Rent payment',
        )

        return game
