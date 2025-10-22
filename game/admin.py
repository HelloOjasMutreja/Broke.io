from django.contrib import admin
from .models import (
    Board, Tile, BoardTile, City, Game, Player, LobbyPlayer,
    GameBoardTileState, Turn, ActionLog, Trade, Bid, ChatMessage
)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'size', 'theme', 'created_at')
    list_filter = ('theme', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Tile)
class TileAdmin(admin.ModelAdmin):
    list_display = ('title', 'tile_type', 'created_at')
    list_filter = ('tile_type', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)


@admin.register(BoardTile)
class BoardTileAdmin(admin.ModelAdmin):
    list_display = ('board', 'position', 'tile')
    list_filter = ('board',)
    search_fields = ('tile__title', 'board__name')
    raw_id_fields = ('board', 'tile')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('tile', 'country', 'base_price', 'mortgage_value', 'color_group')
    list_filter = ('country', 'color_group')
    search_fields = ('tile__title', 'country', 'color_group')
    raw_id_fields = ('tile',)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('public_id', 'name', 'owner', 'status', 'board', 'max_players', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'public_id', 'uuid', 'owner__username')
    readonly_fields = ('uuid', 'public_id', 'created_at', 'started_at', 'finished_at')
    raw_id_fields = ('board', 'owner')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'is_ai', 'created_at')
    list_filter = ('is_ai', 'created_at')
    search_fields = ('display_name', 'user__username')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user',)


@admin.register(LobbyPlayer)
class LobbyPlayerAdmin(admin.ModelAdmin):
    list_display = ('player', 'game', 'seat_index', 'cash', 'position', 'is_ready', 'is_owner')
    list_filter = ('is_ready', 'is_owner', 'game')
    search_fields = ('player__display_name', 'game__name', 'game__public_id')
    readonly_fields = ('joined_at',)
    raw_id_fields = ('game', 'player')


@admin.register(GameBoardTileState)
class GameBoardTileStateAdmin(admin.ModelAdmin):
    list_display = ('game', 'position', 'board_tile', 'owner', 'houses', 'mortgaged')
    list_filter = ('game', 'mortgaged', 'houses')
    search_fields = ('board_tile__tile__title', 'game__name', 'game__public_id')
    readonly_fields = ('last_rent_collected_at',)
    raw_id_fields = ('game', 'board_tile', 'owner')


@admin.register(Turn)
class TurnAdmin(admin.ModelAdmin):
    list_display = ('game', 'current_player', 'round_number', 'created_at')
    list_filter = ('game', 'round_number')
    search_fields = ('game__name', 'game__public_id', 'current_player__display_name')
    readonly_fields = ('created_at',)
    raw_id_fields = ('game', 'current_player')


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('game', 'player', 'action_type', 'created_at')
    list_filter = ('action_type', 'created_at', 'game')
    search_fields = ('game__name', 'game__public_id', 'player__display_name', 'action_type')
    readonly_fields = ('created_at',)
    raw_id_fields = ('game', 'player')


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('game', 'offered_by', 'offered_to', 'accepted', 'created_at')
    list_filter = ('accepted', 'created_at', 'game')
    search_fields = ('game__name', 'game__public_id', 'offered_by__display_name', 'offered_to__display_name')
    readonly_fields = ('created_at',)
    raw_id_fields = ('game', 'offered_by', 'offered_to')


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('game', 'player', 'board_tile_state', 'amount', 'created_at')
    list_filter = ('game', 'created_at')
    search_fields = ('game__name', 'game__public_id', 'player__display_name')
    readonly_fields = ('created_at',)
    raw_id_fields = ('game', 'player', 'board_tile_state')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('game', 'player', 'is_system', 'short_message', 'created_at')
    list_filter = ('is_system', 'created_at', 'game')
    search_fields = ('game__name', 'game__public_id', 'player__display_name', 'message')
    readonly_fields = ('created_at',)
    raw_id_fields = ('game', 'player')

    def short_message(self, obj):
        return (obj.message[:60] + '...') if len(obj.message) > 60 else obj.message
    short_message.short_description = 'Message'
