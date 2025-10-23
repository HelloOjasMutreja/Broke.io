# models.py
import uuid
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class GameMode(models.TextChoices):
    SOLO = "SOLO", "Solo"
    FRIENDS = "FRIENDS", "Friends"
    ONLINE = "ONLINE", "Online"

class TileType(models.TextChoices):
    """
    Tile types for non-property tiles. CITY has been removed - use City model instead.
    Properties/cities are handled via the City model with a OneToOne relationship to Tile.
    """
    UTILITY = "UTILITY", "Utility"
    CHANCE = "CHANCE", "Chance"
    TREASURE = "TREASURE", "Treasure"
    TAX = "TAX", "Tax"
    START = "START", "Start"
    JAIL = "JAIL", "Jail"
    GO_TO_JAIL = "GO_TO_JAIL", "GoToJail"
    FREE_PARKING = "FREE_PARKING", "FreeParking"
    VACATION = "VACATION", "Vacation"
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
    
    def initialize_positions(self):
        """
        Initialize or update board positions with canonical special tiles.
        This is idempotent and transactional - safe to call multiple times.
        
        Creates BoardPosition entries for all positions that don't exist yet,
        and ensures special positions (start, prison, vacation, go_to_prison) 
        have the appropriate canonical tiles.
        
        Does NOT overwrite existing custom positions.
        """
        from django.db import transaction
        
        with transaction.atomic():
            special_pos = self.default_special_positions()
            total_positions = self.total_tiles
            
            # Get or create canonical special tiles
            special_tiles = {
                "start": Tile.objects.get_or_create(
                    title="Start",
                    tile_type=TileType.START,
                    defaults={
                        "description": "Collect salary when passing",
                        "action": {"type": "collect", "amount": 200}
                    }
                )[0],
                "prison": Tile.objects.get_or_create(
                    title="Prison/Visiting",
                    tile_type=TileType.JAIL,
                    defaults={
                        "description": "Just visiting or in jail",
                        "action": {"type": "jail_check"}
                    }
                )[0],
                "vacation": Tile.objects.get_or_create(
                    title="Vacation",
                    tile_type=TileType.VACATION,
                    defaults={
                        "description": "Take a vacation",
                        "action": {"type": "rest"}
                    }
                )[0],
                "go_to_prison": Tile.objects.get_or_create(
                    title="Go to Prison",
                    tile_type=TileType.GO_TO_JAIL,
                    defaults={
                        "description": "Go directly to prison",
                        "action": {"type": "send_to_jail", "target_position": special_pos["prison"]}
                    }
                )[0],
            }
            
            # Get existing positions for this board
            existing_positions = set(
                BoardPosition.objects.filter(board=self).values_list('position', flat=True)
            )
            
            # Create BoardPosition entries for missing positions
            positions_to_create = []
            for pos in range(total_positions):
                if pos in existing_positions:
                    continue  # Don't overwrite existing positions
                
                # Check if this is a special position
                tile_for_pos = None
                for key, special_pos_idx in special_pos.items():
                    if pos == special_pos_idx:
                        tile_for_pos = special_tiles[key]
                        break
                
                if tile_for_pos:
                    # This is a special position - auto-populate with canonical tile
                    positions_to_create.append(
                        BoardPosition(board=self, position=pos, tile=tile_for_pos)
                    )
                # For non-special positions, we don't create entries automatically
                # They should be populated by game designers or left empty
            
            if positions_to_create:
                BoardPosition.objects.bulk_create(positions_to_create)

class Tile(models.Model):
    """
    A canonical tile entity representing non-property tiles (START, JAIL, CHANCE, etc.).
    Position is NOT stored here - it belongs to BoardPosition which maps tiles to board positions.
    This is reusable across boards (multiple boards may reference the same Tile at different positions).
    For property tiles, use City model with OneToOne relationship to Tile.
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

# This model maps a position on a Board to either a Tile or a City.
class BoardPosition(models.Model):
    """
    Maps a board position to either a canonical Tile (for non-property tiles like START, JAIL)
    or a City (for property tiles). Exactly one of (tile, city) must be set.
    
    This is the board-placement layer that connects board positions to game content.
    Multiple Game instances can reference the same Board and its BoardPositions.
    """
    board = models.ForeignKey(Board, related_name="positions", on_delete=models.CASCADE)
    position = models.PositiveIntegerField(
        help_text="Position index on the board. Must be in range [0, board.size*board.size - 1]."
    )
    # Exactly one of these must be set (validated in clean())
    tile = models.ForeignKey(
        Tile, 
        related_name="board_positions", 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Reference to a non-property tile (START, JAIL, CHANCE, etc.)"
    )
    city = models.ForeignKey(
        'City',  # String reference to avoid circular import issues
        related_name="board_positions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Reference to a property/city tile"
    )
    # optional: allow position-specific overrides (e.g., custom action for this placement)
    override_action = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("board", "position")
        ordering = ["position"]

    def clean(self):
        """Validate that exactly one of (tile, city) is set."""
        from django.core.exceptions import ValidationError
        
        if self.tile is None and self.city is None:
            raise ValidationError("BoardPosition must have either a tile or a city set.")
        if self.tile is not None and self.city is not None:
            raise ValidationError("BoardPosition cannot have both tile and city set.")
    
    def save(self, *args, **kwargs):
        """Override save to call full_clean for validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        content = self.tile.title if self.tile else (self.city.tile.title if self.city else "Empty")
        return f"{self.board.name} @ {self.position} -> {content}"

# Legacy model - kept for backwards compatibility during migration
class BoardTile(models.Model):
    """
    DEPRECATED: Legacy model kept for backwards compatibility.
    Use BoardPosition instead for new code.
    
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
    mode = models.CharField(max_length=20, choices=GameMode.choices, default=GameMode.ONLINE)
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
    def get_active_players_count(self):
        """
        Get the number of active players in the game.
        """
        return self.lobby_players.count()
    
    def is_full(self):
        """
        Check if the game is at maximum capacity.
        """
        return self.get_active_players_count() >= self.max_players
    
    def can_user_join(self, user):
        """
        Check if a user can join this game.
        A user can join if:
        - The game is in LOBBY status
        - The game is not full
        - The user is not already in the game
        - For FRIENDS mode, user must be owner or explicitly invited (for now, we'll allow if not full)
        """
        if self.status != GameStatus.LOBBY:
            return False
        if self.is_full():
            return False
        if user is None or not user.is_authenticated:
            return False
        # Check if user already has a player in this game
        if Player.objects.filter(user=user, game_slots__game=self).exists():
            return False
        return True

    def players(self):
        return self.lobby_players.select_related("player").order_by("seat_index")

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
        Create per-game GameBoardTileState entries for each position on the board
        so ownership and development are tracked per game, not globally. 
        Called at game start.
        
        Works with both BoardPosition (new) and BoardTile (legacy) for backwards compatibility.
        """
        # Prevent double init
        if GameBoardTileState.objects.filter(game=self).exists():
            return

        # Try new schema first (BoardPosition)
        board_positions = BoardPosition.objects.filter(board=self.board).order_by("position")
        if board_positions.exists():
            states = []
            for bp in board_positions:
                states.append(GameBoardTileState(
                    game=self, 
                    board_position=bp, 
                    position=bp.position
                ))
            GameBoardTileState.objects.bulk_create(states)
        else:
            # Fallback to legacy schema (BoardTile)
            board_tiles = BoardTile.objects.filter(board=self.board).order_by("position")
            states = []
            for bt in board_tiles:
                states.append(GameBoardTileState(
                    game=self, 
                    board_tile=bt, 
                    position=bt.position
                ))
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
    Per-game state for each board position: who owns it, how many houses, is mortgaged, etc.
    This allows the same position used across multiple games to have separate states.
    
    Links to BoardPosition (new) or BoardTile (legacy) for backwards compatibility.
    """
    game = models.ForeignKey(Game, related_name="tile_states", on_delete=models.CASCADE)
    # New field: reference to BoardPosition
    board_position = models.ForeignKey(
        BoardPosition,
        related_name="game_states",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Reference to BoardPosition (new schema)"
    )
    # Legacy field: kept for backwards compatibility
    board_tile = models.ForeignKey(
        BoardTile,
        related_name="game_states",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="DEPRECATED: Use board_position instead"
    )
    position = models.PositiveIntegerField()
    owner = models.ForeignKey(Player, related_name="owned_tiles", null=True, blank=True, on_delete=models.SET_NULL)
    houses = models.PositiveSmallIntegerField(default=0)  # 0..4 houses, 5 considered hotel if you like
    mortgaged = models.BooleanField(default=False)
    last_rent_collected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("game", "position")
        ordering = ["position"]

    def __str__(self):
        # Try to get title from board_position or board_tile
        if self.board_position:
            title = self.board_position.tile.title if self.board_position.tile else (
                self.board_position.city.tile.title if self.board_position.city else "Unknown"
            )
        elif self.board_tile:
            title = self.board_tile.tile.title
        else:
            title = "Unknown"
        return f"State: {title} @ {self.position} in {self.game.public_id}"

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


# -------------------------------------
# Signals for auto-initialization
# -------------------------------------
@receiver(post_save, sender=Board)
def auto_initialize_board_positions(sender, instance, created, **kwargs):
    """
    Auto-initialize board positions when a new Board is created.
    This ensures special positions (START, JAIL, etc.) are populated automatically.
    """
    if created:
        # Run initialization in a separate transaction to avoid conflicts
        transaction.on_commit(lambda: instance.initialize_positions())
