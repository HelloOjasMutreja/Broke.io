from django.contrib import admin
from .models import (
    Board, Game, Player, City, Tile, Resource,
    Action, Turn, Trade, PowerUp
)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'width', 'height', 'theme', 'is_active', 'created_at')
    list_filter = ('theme', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'mode', 'status', 'board', 'max_players', 'winner', 'created_at')
    list_filter = ('mode', 'status', 'victory_condition', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('board', 'winner')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'money', 'score', 'level', 'is_active', 'turn_order')
    list_filter = ('is_human', 'is_active', 'is_in_jail', 'game')
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'game')


@admin.register(Tile)
class TileAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'terrain_type', 'owner', 'price', 'rent', 'is_mortgaged')
    list_filter = ('terrain_type', 'color_group', 'is_mortgaged', 'board')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('board', 'owner')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'player', 'level', 'population', 'defense', 'health', 'is_capital')
    list_filter = ('level', 'is_capital', 'player')
    search_fields = ('name', 'player__name')
    readonly_fields = ('founded_at', 'updated_at')
    raw_id_fields = ('tile', 'player')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('player', 'resource_type', 'amount', 'capacity', 'production_rate', 'consumption_rate')
    list_filter = ('resource_type', 'player')
    search_fields = ('player__name',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('player',)


@admin.register(Turn)
class TurnAdmin(admin.ModelAdmin):
    list_display = ('game', 'player', 'turn_number', 'round_number', 'phase', 'is_complete', 'started_at')
    list_filter = ('phase', 'is_complete', 'game')
    search_fields = ('player__name',)
    readonly_fields = ('started_at', 'completed_at')
    raw_id_fields = ('game', 'player')


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('player', 'action_type', 'amount', 'is_successful', 'created_at')
    list_filter = ('action_type', 'is_successful', 'created_at')
    search_fields = ('player__name', 'description')
    readonly_fields = ('created_at',)
    raw_id_fields = ('turn', 'player', 'target_tile', 'target_player')


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('initiator', 'recipient', 'status', 'created_at', 'responded_at')
    list_filter = ('status', 'created_at')
    search_fields = ('initiator__name', 'recipient__name', 'message')
    readonly_fields = ('created_at', 'responded_at', 'completed_at')
    raw_id_fields = ('game', 'initiator', 'recipient')


@admin.register(PowerUp)
class PowerUpAdmin(admin.ModelAdmin):
    list_display = ('name', 'player', 'powerup_type', 'is_active', 'is_used', 'acquired_at')
    list_filter = ('powerup_type', 'is_active', 'is_used', 'acquired_at')
    search_fields = ('name', 'player__name', 'description')
    readonly_fields = ('acquired_at', 'activated_at', 'expires_at')
    raw_id_fields = ('player',)
