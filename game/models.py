# models.py
import uuid
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.validators import MinValueValidator

User = settings.AUTH_USER_MODEL

# -------------------------------------
# Helper choices & small utilities
# -------------------------------------
class GameStatus(models.TextChoices):
    LOBBY = "LOBBY", "Lobby"
    READY = "READY", "ReadyToStart"
    ACTIVE = "ACTIVE", "Active"
    PAUSED = "PAUSED", "Paused"
    FINISHED = "FINISHED", "Finished"

class TileType(models.TextChoices):
    CITY = "CITY", "City"
    UTILITY = "UTILITY", "Utility"
    CHANCE = "CHANCE", "Chance"
    TREASURE = "TREASURE", "Treasure"
    TAX = "TAX", "Tax"
    START = "START", "Start"
    JAIL = "JAIL", "Jail"
    GO_TO_JAIL = "GO_TO_JAIL", "GoToJail"
    FREE_PARKING = "FREE_PARKING", "FreeParking"
    CUSTOM = "CUSTOM", "Custom"

def generate_public_id(length=6):
    # short, human-friendly id like 'ha83sZ'
    return get_random_string(length=length).lower()

# -------------------------------------
# Board and tile canonical data
# -------------------------------------
class Board(models.Model):
    """
    A board definition. Boards have a grid size (n -> total tiles = n*n),
    a theme, and a canonical ordering of positions (0..n*n-1).
    Tiles are attached to boards via BoardTile (a through/instance model).
    """
    name = models.CharField(max_length=120)
    size = models.PositiveIntegerField(
        help_text="n for an n*n board. Valid positions = 0 .. (n*n - 1).",
        validators=[MinValueValidator(2)]
    )
    theme = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.size}x{self.size})"

    @property
    def total_tiles(self) -> int:
        return self.size * self.size

    def default_special_positions(self):
        """
        Returns the canonical special tile positions based on your rules:
          - 0 -> Start
          - (n - 1) -> Prison (pass-by/visiting jail)
          - (2n - 1) -> Vacation (example)
          - (3n - 1) -> Go to Prison
        """
        n = self.size
        return {
            "start": 0,
            "prison": n - 1,
            "vacation": 2 * n - 1,
            "go_to_prison": 3 * n - 1
        }

class Tile(models.Model):
    """
    A canonical tile entity. This is reusable across boards (multiple boards may
    reference the same Tile in multiple positions via BoardTile).
    """
    title = models.CharField(max_length=120)
    tile_type = models.CharField(max_length=20, choices=TileType.choices, default=TileType.CUSTOM)
    description = models.TextField(blank=True)
    # action_json stores the default action sequence or metadata for landing on this tile.
    # Example: {"type":"collect","amount":200} or a script reference key.
    action = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # extensible data
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} [{self.tile_type}]"

# This model maps a Tile to a Board at a specific position.
class BoardTile(models.Model):
    """
    Instances of tiles on a board. A single Tile can appear multiple times on the same board
    or multiple boards. BoardTile is the instance-level representation used in Game sessions.
    """
    board = models.ForeignKey(Board, related_name="board_tiles", on_delete=models.CASCADE)
    tile = models.ForeignKey(Tile, related_name="instances", on_delete=models.CASCADE)
    position = models.PositiveIntegerField(
        help_text="Position index on the board. Must be in range [0, board.size*board.size - 1]."
    )
    # optional: allow tile instance overrides (e.g., custom action for this board placement)
    override_action = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("board", "position")
        ordering = ["position"]

    def __str__(self):
        return f"{self.board.name} @ {self.position} -> {self.tile.title}"

# -------------------------------------
# Tile subtype: City (property)
# -------------------------------------
class City(models.Model):
    """
    City (property) data attached to a Tile. Use OneToOne so a Tile can optionally be a City.
    Rent values stored explicitly for clarity (houses 0..4, hotel as 5).
    """
    tile = models.OneToOneField(Tile, related_name="city", on_delete=models.CASCADE)
    country = models.CharField(max_length=80, blank=True, help_text="Optional locale metadata")
    base_price = models.PositiveIntegerField(default=100)
    mortgage_value = models.PositiveIntegerField(default=50)
    rent_base = models.PositiveIntegerField(default=10)
    rent_house_1 = models.PositiveIntegerField(default=50)
    rent_house_2 = models.PositiveIntegerField(default=150)
    rent_house_3 = models.PositiveIntegerField(default=450)
    rent_house_4 = models.PositiveIntegerField(default=625)
    rent_hotel = models.PositiveIntegerField(default=750)
    house_cost = models.PositiveIntegerField(default=50)
    hotel_cost = models.PositiveIntegerField(default=50)
    color_group = models.CharField(max_length=40, blank=True, help_text="Group e.g., Boardwalk-set")

    def __str__(self):
        return f"City: {self.tile.title} ({self.base_price})"

# -------------------------------------
# Game session + lobby + players
# -------------------------------------
class Game(models.Model):
    """
    A game session. Public id is a short string (human friendly) while 'uuid' is a true UUID.
    The owner can start the game once all players are ready.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    public_id = models.CharField(max_length=12, default=generate_public_id, unique=True)
    name = models.CharField(max_length=140, blank=True)
    owner = models.ForeignKey(User, related_name="owned_games", on_delete=models.SET_NULL, null=True)
    board = models.ForeignKey(Board, related_name="games", on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=GameStatus.choices, default=GameStatus.LOBBY)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    # Configs:
    max_players = models.PositiveSmallIntegerField(default=6)
    allow_spectators = models.BooleanField(default=True)
    # serialized game state (optional): speed vs normalization tradeoff
    state = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Game {self.public_id} ({self.status})"

    # -------------- Lobby & Ready/Start logic --------------
    def players(self):
        return self.lobby_players.select_related("user").order_by("seat_index")

    def all_players_ready(self) -> bool:
        """
        Quick check — doesn't change state; just inspects players.
        """
        players = self.players()
        if not players.exists():
            return False
        return all([p.is_ready for p in players])

    def can_start(self, user) -> bool:
        """
        Only owner can start and only when all players are ready and at least 2 players present.
        """
        if user is None:
            return False
        if self.owner and getattr(user, "pk", None) != getattr(self.owner, "pk", None):
            return False
        player_count = self.players().count()
        return player_count >= 2 and self.all_players_ready()

    @transaction.atomic
    def start(self, user):
        """
        Start the game: set status, timestamp, initialize per-game property states,
        determine turn order, and set first player. This should be an atomic operation.
        """
        if not self.can_start(user):
            raise PermissionError("Owner required and all players must be ready with min players.")
        # initialize state only once
        if self.status != GameStatus.LOBBY:
            raise ValueError("Game already started or finished.")
        # snapshot board layout into game-specific BoardTileState (see below)
        self.initialize_board_state()
        # choose turn order (current simple: seat_index ascending)
        first_player = self.players().order_by("seat_index").first()
        Turn.objects.create(game=self, current_player=first_player.player, round_number=1)
        self.status = GameStatus.ACTIVE
        self.started_at = timezone.now()
        self.save()

    def initialize_board_state(self):
        """
        Create per-game BoardTileState entries for each BoardTile instance so ownership and
        development are tracked per game, not globally. Called at game start.
        """
        # Prevent double init
        if GameBoardTileState.objects.filter(game=self).exists():
            return

        board_tiles = BoardTile.objects.filter(board=self.board).order_by("position")
        states = []
        for bt in board_tiles:
            states.append(GameBoardTileState(game=self, board_tile=bt, position=bt.position))
        GameBoardTileState.objects.bulk_create(states)

# -------------------------------------
# Players & lobby players
# -------------------------------------
class Player(models.Model):
    """
    A player entity that may be tied to a User or be a guest/AI.
    Note: Player is persistent across games; LobbyPlayer links a Player to a Game.
    """
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    display_name = models.CharField(max_length=80)
    is_ai = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or f"Player-{self.pk}"

class LobbyPlayer(models.Model):
    """
    A mapping of a Player into a specific Game's lobby. This is the per-game player state
    visible before and during the match.
    """
    game = models.ForeignKey(Game, related_name="lobby_players", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name="game_slots", on_delete=models.CASCADE)
    seat_index = models.PositiveSmallIntegerField(default=0)
    cash = models.BigIntegerField(default=1500)
    position = models.PositiveIntegerField(default=0)
    is_ready = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("game", "seat_index")
        ordering = ["seat_index"]

    def __str__(self):
        return f"{self.player} in {self.game.public_id} (seat {self.seat_index})"

# -------------------------------------
# Per-game board tile state (ownership & development)
# -------------------------------------
class GameBoardTileState(models.Model):
    """
    Per-game state for each BoardTile instance: who owns it, how many houses, is mortgaged, etc.
    This allows the same Tile used across multiple games/boards to have separate states.
    """
    game = models.ForeignKey(Game, related_name="tile_states", on_delete=models.CASCADE)
    board_tile = models.ForeignKey(BoardTile, related_name="game_states", on_delete=models.CASCADE)
    position = models.PositiveIntegerField()
    owner = models.ForeignKey(Player, related_name="owned_tiles", null=True, blank=True, on_delete=models.SET_NULL)
    houses = models.PositiveSmallIntegerField(default=0)  # 0..4 houses, 5 considered hotel if you like
    mortgaged = models.BooleanField(default=False)
    last_rent_collected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("game", "position")
        ordering = ["position"]

    def __str__(self):
        return f"State: {self.board_tile.tile.title} @ {self.position} in {self.game.public_id}"

# -------------------------------------
# Turn, Action, Trade, Bid, Chat
# -------------------------------------
class Turn(models.Model):
    """
    Tracks the current turn for a game. There will typically be one active Turn row at a time.
    """
    game = models.ForeignKey(Game, related_name="turns", on_delete=models.CASCADE)
    current_player = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL)
    round_number = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.game.public_id} Round {self.round_number} - {self.current_player}"

class ActionLog(models.Model):
    """
    Record of actions taken by players. Used for auditing, replay, and deterministic replay in multiplayer.
    """
    game = models.ForeignKey(Game, related_name="actions", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL)
    action_type = models.CharField(max_length=80)
    payload = models.JSONField(default=dict, blank=True)  # structured details (e.g., {"from":..., "to":..., "amount":...})
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

class Trade(models.Model):
    """
    A trade offer between players. Uses JSON for flexibility (properties, cash, cards).
    """
    game = models.ForeignKey(Game, related_name="trades", on_delete=models.CASCADE)
    offered_by = models.ForeignKey(Player, related_name="outgoing_trades", on_delete=models.CASCADE)
    offered_to = models.ForeignKey(Player, related_name="incoming_trades", null=True, blank=True, on_delete=models.CASCADE)
    offered = models.JSONField(default=dict)    # e.g., {"cash":100, "tiles":[position,...]}
    requested = models.JSONField(default=dict)  # e.g., {"cash":400, "tiles":[...]}
    accepted = models.BooleanField(null=True, default=None)  # None = pending, True = accepted, False = rejected
    created_at = models.DateTimeField(auto_now_add=True)

class Bid(models.Model):
    """
    Auction bids for a tile. Each bid references the GameBoardTileState (or board_tile) being auctioned.
    """
    game = models.ForeignKey(Game, related_name="bids", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    board_tile_state = models.ForeignKey(GameBoardTileState, null=True, on_delete=models.SET_NULL)
    amount = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    """
    In-game chat.
    """
    game = models.ForeignKey(Game, related_name="messages", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_system = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
