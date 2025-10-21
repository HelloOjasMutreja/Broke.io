from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import uuid


class Board(models.Model):
    """
    Represents the game world or grid layout for a strategy board game.
    Each board defines the physical space where gameplay occurs with configurable dimensions.
    """
    name = models.CharField(
        max_length=200,
        verbose_name="Board Name",
        help_text="Name of the game board"
    )
    width = models.PositiveIntegerField(
        default=11,
        validators=[MinValueValidator(5), MaxValueValidator(50)],
        verbose_name="Board Width",
        help_text="Width of the board in tiles"
    )
    height = models.PositiveIntegerField(
        default=11,
        validators=[MinValueValidator(5), MaxValueValidator(50)],
        verbose_name="Board Height",
        help_text="Height of the board in tiles"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Description of the board layout and theme"
    )
    theme = models.CharField(
        max_length=50,
        choices=[
            ('classic', 'Classic'),
            ('cyber', 'Cyber'),
            ('fantasy', 'Fantasy'),
            ('space', 'Space'),
        ],
        default='classic',
        verbose_name="Theme"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether this board is available for new games"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Board"
        verbose_name_plural = "Boards"

    def __str__(self):
        return f"{self.name} ({self.width}x{self.height})"

    def get_total_tiles(self):
        """Returns the total number of tiles on the board."""
        return self.width * self.height


class Game(models.Model):
    """
    Manages game sessions, states, and configurations for a strategy board game.
    Each game represents a unique play session with specific rules and settings.
    """
    STATUS_CHOICES = [
        ('waiting', 'Waiting for Players'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    MODE_CHOICES = [
        ('solo', 'Solo'),
        ('friends', 'Friends'),
        ('online', 'Online'),
    ]

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="Game UUID",
        help_text="Unique identifier for this game session",
        db_index=True
    )
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='games',
        verbose_name="Board"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_games',
        verbose_name="Game Owner",
        help_text="User who created this game and can start it"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Game Name",
        help_text="Name of this game session"
    )
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default='solo',
        verbose_name="Game Mode"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='waiting',
        verbose_name="Game Status"
    )
    max_players = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(2), MaxValueValidator(8)],
        verbose_name="Maximum Players"
    )
    turn_time_limit = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(30)],
        verbose_name="Turn Time Limit (seconds)",
        help_text="Time limit for each turn in seconds"
    )
    starting_money = models.PositiveIntegerField(
        default=1500,
        verbose_name="Starting Money",
        help_text="Amount of money each player starts with"
    )
    victory_condition = models.CharField(
        max_length=100,
        choices=[
            ('last_standing', 'Last Player Standing'),
            ('most_wealth', 'Most Wealth'),
            ('territory_control', 'Territory Control'),
            ('points', 'Points'),
        ],
        default='last_standing',
        verbose_name="Victory Condition"
    )
    winner = models.ForeignKey(
        'Player',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_games',
        verbose_name="Winner"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Started At"
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ended At"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Game"
        verbose_name_plural = "Games"
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['mode', 'status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_mode_display()}) - {self.get_status_display()}"

    def get_active_players_count(self):
        """Returns the number of active players in the game."""
        return self.players.filter(is_active=True).count()

    def is_full(self):
        """Checks if the game has reached maximum players."""
        return self.get_active_players_count() >= self.max_players

    def can_start(self):
        """Checks if the game can be started."""
        if self.status != 'waiting':
            return False
        if self.get_active_players_count() < 2:
            return False
        # Check if all players are ready
        return all(player.is_ready for player in self.players.filter(is_active=True))
    
    def all_players_ready(self):
        """Checks if all players are marked as ready."""
        active_players = self.players.filter(is_active=True)
        if active_players.count() < 2:
            return False
        return all(player.is_ready for player in active_players)


class Player(models.Model):
    """
    Holds player identity, stats, and relationships to the game.
    Represents a participant in a game session with their current state and statistics.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='game_players',
        null=True,
        blank=True,
        verbose_name="User",
        help_text="Associated user account (null for AI players)"
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='players',
        verbose_name="Game"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Player Name"
    )
    token = models.CharField(
        max_length=10,
        default='🚗',
        verbose_name="Player Token",
        help_text="Visual representation of the player"
    )
    is_human = models.BooleanField(
        default=True,
        verbose_name="Is Human",
        help_text="Whether this is a human player or AI"
    )
    money = models.IntegerField(
        default=1500,
        verbose_name="Money",
        help_text="Current money/currency balance"
    )
    position = models.PositiveIntegerField(
        default=0,
        verbose_name="Board Position",
        help_text="Current position on the board"
    )
    score = models.IntegerField(
        default=0,
        verbose_name="Score",
        help_text="Player's current score"
    )
    experience = models.PositiveIntegerField(
        default=0,
        verbose_name="Experience Points"
    )
    level = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Level"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether the player is still in the game"
    )
    is_ready = models.BooleanField(
        default=False,
        verbose_name="Is Ready",
        help_text="Whether the player is ready to start the game"
    )
    is_in_jail = models.BooleanField(
        default=False,
        verbose_name="In Jail"
    )
    turn_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Turn Order",
        help_text="Order in which this player takes turns"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Player Color",
        help_text="Color associated with this player"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    class Meta:
        ordering = ['game', 'turn_order']
        verbose_name = "Player"
        verbose_name_plural = "Players"
        unique_together = [['game', 'turn_order']]
        indexes = [
            models.Index(fields=['game', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} in {self.game.name}"

    def add_money(self, amount):
        """Adds money to the player's balance."""
        self.money += amount
        self.save(update_fields=['money', 'updated_at'])

    def remove_money(self, amount):
        """Removes money from the player's balance."""
        self.money -= amount
        self.save(update_fields=['money', 'updated_at'])

    def add_experience(self, amount):
        """Adds experience points and handles level ups."""
        self.experience += amount
        # Simple level calculation: level up every 100 XP
        new_level = (self.experience // 100) + 1
        if new_level > self.level:
            self.level = new_level
        self.save(update_fields=['experience', 'level', 'updated_at'])
    
    def toggle_ready(self):
        """Toggles the player's ready state."""
        self.is_ready = not self.is_ready
        self.save(update_fields=['is_ready', 'updated_at'])
        return self.is_ready


class Tile(models.Model):
    """
    Defines grid tiles on the board with terrain type, position, ownership, and resource yield.
    Each tile represents a specific location on the game board with unique properties.
    """
    TERRAIN_CHOICES = [
        ('property', 'Property'),
        ('railroad', 'Railroad'),
        ('utility', 'Utility'),
        ('corner', 'Corner'),
        ('chance', 'Chance'),
        ('community_chest', 'Community Chest'),
        ('tax', 'Tax'),
        ('go', 'Go'),
        ('jail', 'Jail'),
        ('free_parking', 'Free Parking'),
        ('go_to_jail', 'Go to Jail'),
    ]

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tiles',
        verbose_name="Board"
    )
    position = models.PositiveIntegerField(
        verbose_name="Position",
        help_text="Position on the board (0-39 for standard board)"
    )
    x_coordinate = models.IntegerField(
        verbose_name="X Coordinate",
        help_text="X position in grid"
    )
    y_coordinate = models.IntegerField(
        verbose_name="Y Coordinate",
        help_text="Y position in grid"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Tile Name"
    )
    terrain_type = models.CharField(
        max_length=20,
        choices=TERRAIN_CHOICES,
        default='property',
        verbose_name="Terrain Type"
    )
    owner = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_tiles',
        verbose_name="Owner"
    )
    price = models.PositiveIntegerField(
        default=0,
        verbose_name="Purchase Price"
    )
    rent = models.PositiveIntegerField(
        default=0,
        verbose_name="Rent Amount"
    )
    color_group = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Color Group",
        help_text="Property color group for monopoly bonuses"
    )
    resource_yield = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resource Yield",
        help_text="Resources generated by this tile per turn"
    )
    is_mortgaged = models.BooleanField(
        default=False,
        verbose_name="Is Mortgaged"
    )
    improvement_level = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Improvement Level",
        help_text="Number of houses/hotels (0-5)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    class Meta:
        ordering = ['board', 'position']
        verbose_name = "Tile"
        verbose_name_plural = "Tiles"
        unique_together = [['board', 'position'], ['board', 'x_coordinate', 'y_coordinate']]
        indexes = [
            models.Index(fields=['board', 'terrain_type']),
            models.Index(fields=['owner']),
        ]

    def __str__(self):
        return f"{self.name} at position {self.position}"

    def calculate_rent(self):
        """Calculates the current rent based on improvements and ownership."""
        if self.is_mortgaged or not self.owner:
            return 0
        base_rent = self.rent
        if self.improvement_level > 0:
            return base_rent * (2 ** self.improvement_level)
        return base_rent


class City(models.Model):
    """
    Represents player-built structures with attributes like name, owner, level, resources, and defense.
    Cities are strategic improvements that provide benefits and control territory.
    """
    tile = models.ForeignKey(
        Tile,
        on_delete=models.CASCADE,
        related_name='cities',
        verbose_name="Tile"
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='cities',
        verbose_name="Owner"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="City Name"
    )
    level = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="City Level",
        help_text="Level of development (1-10)"
    )
    population = models.PositiveIntegerField(
        default=100,
        verbose_name="Population"
    )
    defense = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        verbose_name="Defense Points",
        help_text="Defensive strength of the city"
    )
    production_capacity = models.PositiveIntegerField(
        default=10,
        verbose_name="Production Capacity",
        help_text="Resources produced per turn"
    )
    storage_capacity = models.PositiveIntegerField(
        default=100,
        verbose_name="Storage Capacity",
        help_text="Maximum resources that can be stored"
    )
    health = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="City Health",
        help_text="Current health percentage"
    )
    is_capital = models.BooleanField(
        default=False,
        verbose_name="Is Capital",
        help_text="Whether this is the player's capital city"
    )
    founded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Founded At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    class Meta:
        ordering = ['-level', 'name']
        verbose_name = "City"
        verbose_name_plural = "Cities"
        indexes = [
            models.Index(fields=['player', '-level']),
            models.Index(fields=['tile']),
        ]

    def __str__(self):
        return f"{self.name} (Level {self.level}) - {self.player.name}"

    def upgrade(self):
        """Upgrades the city to the next level."""
        if self.level < 10:
            self.level += 1
            self.defense += 5
            self.production_capacity += 10
            self.storage_capacity += 50
            self.save(update_fields=['level', 'defense', 'production_capacity', 'storage_capacity', 'updated_at'])

    def repair(self, amount):
        """Repairs city health."""
        self.health = min(100, self.health + amount)
        self.save(update_fields=['health', 'updated_at'])


class Resource(models.Model):
    """
    Represents resource types (food, gold, energy, etc.) and storage mechanics.
    Resources are essential for building, upgrading, and maintaining game elements.
    """
    RESOURCE_TYPE_CHOICES = [
        ('food', 'Food'),
        ('gold', 'Gold'),
        ('energy', 'Energy'),
        ('wood', 'Wood'),
        ('stone', 'Stone'),
        ('iron', 'Iron'),
        ('gems', 'Gems'),
        ('influence', 'Influence'),
    ]

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name="Player"
    )
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPE_CHOICES,
        verbose_name="Resource Type"
    )
    amount = models.IntegerField(
        default=0,
        verbose_name="Amount",
        help_text="Current amount of this resource"
    )
    capacity = models.PositiveIntegerField(
        default=1000,
        verbose_name="Storage Capacity",
        help_text="Maximum storage capacity for this resource"
    )
    production_rate = models.IntegerField(
        default=0,
        verbose_name="Production Rate",
        help_text="Amount produced per turn"
    )
    consumption_rate = models.IntegerField(
        default=0,
        verbose_name="Consumption Rate",
        help_text="Amount consumed per turn"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    class Meta:
        ordering = ['player', 'resource_type']
        verbose_name = "Resource"
        verbose_name_plural = "Resources"
        unique_together = [['player', 'resource_type']]
        indexes = [
            models.Index(fields=['player', 'resource_type']),
        ]

    def __str__(self):
        return f"{self.player.name} - {self.get_resource_type_display()}: {self.amount}"

    def add(self, amount):
        """Adds resources up to capacity."""
        self.amount = min(self.capacity, self.amount + amount)
        self.save(update_fields=['amount', 'updated_at'])

    def remove(self, amount):
        """Removes resources (can go negative)."""
        self.amount -= amount
        self.save(update_fields=['amount', 'updated_at'])

    def has_sufficient(self, amount):
        """Checks if player has sufficient resources."""
        return self.amount >= amount

    def get_net_rate(self):
        """Returns net production rate (production - consumption)."""
        return self.production_rate - self.consumption_rate


class Turn(models.Model):
    """
    Manages sequence, phase, and round data for turn-based gameplay.
    Each turn represents a specific player's opportunity to act in the game.
    """
    PHASE_CHOICES = [
        ('roll', 'Roll Dice'),
        ('move', 'Move'),
        ('action', 'Take Action'),
        ('trade', 'Trade'),
        ('build', 'Build'),
        ('end', 'End Turn'),
    ]

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='turns',
        verbose_name="Game"
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='turns',
        verbose_name="Player"
    )
    turn_number = models.PositiveIntegerField(
        verbose_name="Turn Number",
        help_text="Sequential turn number in the game"
    )
    round_number = models.PositiveIntegerField(
        verbose_name="Round Number",
        help_text="Game round (one round = all players take a turn)"
    )
    phase = models.CharField(
        max_length=20,
        choices=PHASE_CHOICES,
        default='roll',
        verbose_name="Turn Phase"
    )
    dice_roll = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Dice Roll",
        help_text="Dice roll results for this turn"
    )
    actions_taken = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Actions Taken",
        help_text="List of actions performed during this turn"
    )
    is_complete = models.BooleanField(
        default=False,
        verbose_name="Is Complete"
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Started At"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Completed At"
    )

    class Meta:
        ordering = ['game', '-turn_number']
        verbose_name = "Turn"
        verbose_name_plural = "Turns"
        unique_together = [['game', 'turn_number']]
        indexes = [
            models.Index(fields=['game', '-turn_number']),
            models.Index(fields=['player', '-started_at']),
        ]

    def __str__(self):
        return f"Turn {self.turn_number} (Round {self.round_number}) - {self.player.name}"

    def complete(self):
        """Marks the turn as complete."""
        if not self.is_complete:
            self.is_complete = True
            self.completed_at = models.functions.Now()
            self.save(update_fields=['is_complete', 'completed_at'])


class Action(models.Model):
    """
    Stores player moves, events, or turn-based actions.
    Actions represent specific activities performed by players during gameplay.
    """
    ACTION_TYPE_CHOICES = [
        ('move', 'Move'),
        ('buy', 'Buy Property'),
        ('sell', 'Sell Property'),
        ('trade', 'Trade'),
        ('build', 'Build'),
        ('upgrade', 'Upgrade'),
        ('attack', 'Attack'),
        ('defend', 'Defend'),
        ('collect', 'Collect Resources'),
        ('pay', 'Pay'),
        ('roll_dice', 'Roll Dice'),
        ('draw_card', 'Draw Card'),
        ('use_powerup', 'Use Powerup'),
        ('pass', 'Pass Turn'),
    ]

    turn = models.ForeignKey(
        Turn,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name="Turn"
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name="Player"
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPE_CHOICES,
        verbose_name="Action Type"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Detailed description of the action"
    )
    target_tile = models.ForeignKey(
        Tile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actions',
        verbose_name="Target Tile"
    )
    target_player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='targeted_actions',
        verbose_name="Target Player"
    )
    amount = models.IntegerField(
        default=0,
        verbose_name="Amount",
        help_text="Monetary or resource amount involved"
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Action Data",
        help_text="Additional action-specific data"
    )
    is_successful = models.BooleanField(
        default=True,
        verbose_name="Is Successful",
        help_text="Whether the action was successful"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Action"
        verbose_name_plural = "Actions"
        indexes = [
            models.Index(fields=['player', '-created_at']),
            models.Index(fields=['turn', 'action_type']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.player.name} - {self.get_action_type_display()} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Trade(models.Model):
    """
    Manages trading between players for resources, properties, and money.
    Facilitates economic interactions between players.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='trades',
        verbose_name="Game"
    )
    initiator = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='initiated_trades',
        verbose_name="Initiator"
    )
    recipient = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='received_trades',
        verbose_name="Recipient"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trade Status"
    )
    initiator_offer = models.JSONField(
        default=dict,
        verbose_name="Initiator Offer",
        help_text="What the initiator is offering (money, resources, properties)"
    )
    recipient_offer = models.JSONField(
        default=dict,
        verbose_name="Recipient Offer",
        help_text="What the recipient is offering in return"
    )
    message = models.TextField(
        blank=True,
        verbose_name="Message",
        help_text="Optional message with the trade offer"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Responded At"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Completed At"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Trade"
        verbose_name_plural = "Trades"
        indexes = [
            models.Index(fields=['initiator', 'status']),
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Trade: {self.initiator.name} ↔ {self.recipient.name} ({self.get_status_display()})"


class PowerUp(models.Model):
    """
    Represents special abilities or temporary bonuses that players can acquire and use.
    PowerUps add strategic depth and variety to gameplay.
    """
    POWERUP_TYPE_CHOICES = [
        ('double_rent', 'Double Rent'),
        ('immunity', 'Immunity'),
        ('fast_travel', 'Fast Travel'),
        ('discount', 'Purchase Discount'),
        ('steal', 'Steal Property'),
        ('protection', 'Protection Shield'),
        ('boost', 'Resource Boost'),
        ('vision', 'Reveal Information'),
    ]

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='powerups',
        verbose_name="Player"
    )
    powerup_type = models.CharField(
        max_length=20,
        choices=POWERUP_TYPE_CHOICES,
        verbose_name="PowerUp Type"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="PowerUp Name"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="What this powerup does"
    )
    duration = models.PositiveIntegerField(
        default=1,
        verbose_name="Duration (turns)",
        help_text="Number of turns this powerup lasts"
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name="Is Active",
        help_text="Whether this powerup is currently active"
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name="Is Used",
        help_text="Whether this powerup has been used"
    )
    acquired_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Acquired At"
    )
    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Activated At"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expires At"
    )

    class Meta:
        ordering = ['-acquired_at']
        verbose_name = "PowerUp"
        verbose_name_plural = "PowerUps"
        indexes = [
            models.Index(fields=['player', 'is_active']),
            models.Index(fields=['player', 'is_used']),
        ]

    def __str__(self):
        return f"{self.name} - {self.player.name}"

    def activate(self):
        """Activates the powerup."""
        if not self.is_used:
            self.is_active = True
            self.is_used = True
            self.activated_at = models.functions.Now()
            self.save(update_fields=['is_active', 'is_used', 'activated_at'])

    def deactivate(self):
        """Deactivates the powerup."""
        if self.is_active:
            self.is_active = False
            self.expires_at = models.functions.Now()
            self.save(update_fields=['is_active', 'expires_at'])


class ChatMessage(models.Model):
    """
    Simple in-game chat messages and system notifications.
    Stored per game and optionally linked to a player; supports message types.
    """
    MESSAGE_TYPE_CHOICES = [
        ('player', 'Player'),
        ('system', 'System'),
        ('game', 'Game'),
    ]

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name='Game'
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_messages',
        verbose_name='Player'
    )
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES,
        default='player',
        verbose_name='Message Type'
    )
    content = models.TextField(verbose_name='Content')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        indexes = [
            models.Index(fields=['game', '-created_at']),
            models.Index(fields=['player', '-created_at']),
            models.Index(fields=['message_type']),
        ]

    def __str__(self):
        prefix = self.player.name if self.player else self.get_message_type_display()
        return f"[{self.created_at:%H:%M}] {prefix}: {self.content[:40]}"


class Auction(models.Model):
    """
    Property auction model for unpurchased tiles or trades.
    Supports live bidding and tracking highest bid/bidder.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ]

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='auctions',
        verbose_name='Game'
    )
    tile = models.ForeignKey(
        Tile,
        on_delete=models.CASCADE,
        related_name='auctions',
        verbose_name='Tile'
    )
    started_by = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='started_auctions',
        verbose_name='Started By'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    starting_price = models.PositiveIntegerField(default=0, verbose_name='Starting Price')
    current_price = models.PositiveIntegerField(default=0, verbose_name='Current Price')
    highest_bidder = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_auctions',
        verbose_name='Highest Bidder'
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Started At')
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name='Ends At')

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Auction'
        verbose_name_plural = 'Auctions'
        indexes = [
            models.Index(fields=['game', 'status']),
            models.Index(fields=['tile']),
            models.Index(fields=['-started_at']),
        ]

    def __str__(self):
        return f"Auction for {self.tile.name} ({self.get_status_display()})"

    def place_bid(self, bidder: 'Player', amount: int) -> 'Bid':
        """Place a bid; validates auction status, amount, and bidder funds."""
        if self.status != 'active':
            raise ValidationError('Auction is not active')
        if amount <= max(self.current_price, self.starting_price):
            raise ValidationError('Bid must be higher than current price')
        if bidder.game_id != self.game_id:
            raise ValidationError('Bidder must be in the same game')
        if bidder.money < amount:
            raise ValidationError('Insufficient funds for this bid')

        bid = Bid.objects.create(auction=self, bidder=bidder, amount=amount)
        self.current_price = amount
        self.highest_bidder = bidder
        self.save(update_fields=['current_price', 'highest_bidder', 'started_at'])
        return bid

    def end(self):
        """End the auction and transfer ownership if there's a winner."""
        if self.status != 'active':
            return
        self.status = 'ended'
        self.ends_at = models.functions.Now()
        self.save(update_fields=['status', 'ends_at'])

        if self.highest_bidder and self.current_price > 0:
            # Transfer money and ownership
            winner = self.highest_bidder
            if winner.money >= self.current_price and self.tile.owner is None:
                winner.remove_money(self.current_price)
                self.tile.owner = winner
                self.tile.save(update_fields=['owner', 'updated_at'])


class Bid(models.Model):
    """Individual bid record for an Auction."""
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name='bids',
        verbose_name='Auction'
    )
    bidder = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='bids',
        verbose_name='Bidder'
    )
    amount = models.PositiveIntegerField(verbose_name='Amount')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bid'
        verbose_name_plural = 'Bids'
        indexes = [
            models.Index(fields=['auction', '-created_at']),
            models.Index(fields=['bidder']),
        ]

    def __str__(self):
        return f"{self.bidder.name} bid {self.amount} on {self.auction.tile.name}"


class Card(models.Model):
    """Chance/Community Chest style cards with an effect payload."""
    DECK_CHOICES = [
        ('chance', 'Chance'),
        ('community', 'Community Chest'),
    ]

    deck = models.CharField(max_length=20, choices=DECK_CHOICES, verbose_name='Deck')
    title = models.CharField(max_length=100, verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')
    effect = models.JSONField(default=dict, blank=True, verbose_name='Effect')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')

    class Meta:
        ordering = ['deck', 'order', 'id']
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'
        indexes = [
            models.Index(fields=['deck', 'is_active', 'order']),
        ]

    def __str__(self):
        return f"{self.get_deck_display()}: {self.title}"


class Minigame(models.Model):
    """Tracks a minigame session and its outcome for a player."""
    TYPE_CHOICES = [
        ('target_click', 'Target Click'),
        ('memory_match', 'Memory Match'),
        ('quick_math', 'Quick Math'),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='minigames', verbose_name='Game')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='minigames', verbose_name='Player')
    minigame_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Minigame Type')
    score = models.IntegerField(default=0, verbose_name='Score')
    reward = models.IntegerField(default=0, verbose_name='Reward')
    is_completed = models.BooleanField(default=False, verbose_name='Is Completed')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Started At')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Completed At')

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Minigame'
        verbose_name_plural = 'Minigames'
        indexes = [
            models.Index(fields=['game', 'minigame_type']),
            models.Index(fields=['player', '-started_at']),
        ]

    def __str__(self):
        return f"{self.player.name} - {self.get_minigame_type_display()} ({self.score})"

    def complete(self, reward: int = 0):
        self.is_completed = True
        self.reward = reward
        self.completed_at = models.functions.Now()
        self.save(update_fields=['is_completed', 'reward', 'completed_at'])
        if reward:
            self.player.add_money(reward)


class Transaction(models.Model):
    """
    Ledger entries for money/resource transfers to aid auditing and histories.
    """
    KIND_CHOICES = [
        ('money', 'Money'),
        ('resource', 'Resource'),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='transactions', verbose_name='Game')
    from_player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='outgoing_transactions',
        verbose_name='From'
    )
    to_player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incoming_transactions',
        verbose_name='To'
    )
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default='money', verbose_name='Kind')
    amount = models.IntegerField(default=0, verbose_name='Amount')
    resource_type = models.CharField(max_length=20, blank=True, verbose_name='Resource Type')
    reason = models.CharField(max_length=100, blank=True, verbose_name='Reason')
    related_action = models.ForeignKey(
        'Action',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name='Related Action'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['game', '-created_at']),
            models.Index(fields=['from_player']),
            models.Index(fields=['to_player']),
            models.Index(fields=['kind']),
        ]

    def __str__(self):
        direction = f"{self.from_player and self.from_player.name} -> {self.to_player and self.to_player.name}"
        return f"{self.get_kind_display()} {self.amount} ({direction})"
