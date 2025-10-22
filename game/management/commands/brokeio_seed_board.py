"""
Management command to initialize or re-initialize board positions.

Usage:
    python manage.py brokeio_seed_board --board-id=<id>
    python manage.py brokeio_seed_board --board-id=1 --force

This command:
- Creates BoardPosition entries for all special positions (start, prison, vacation, go_to_prison)
- Is idempotent: safe to run multiple times
- Does NOT overwrite existing custom positions unless --force is used
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from game.models import Board, BoardPosition


class Command(BaseCommand):
    help = 'Initialize or re-initialize board positions with canonical special tiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--board-id',
            type=int,
            required=True,
            help='ID of the board to initialize',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-initialization (clears existing positions)',
        )

    def handle(self, *args, **options):
        board_id = options['board_id']
        force = options['force']

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise CommandError(f'Board with id={board_id} does not exist')

        self.stdout.write(
            self.style.SUCCESS(f'Processing board: {board.name} (id={board.id})')
        )

        if force:
            self.stdout.write(
                self.style.WARNING('Force mode enabled - clearing existing positions...')
            )
            with transaction.atomic():
                deleted_count = BoardPosition.objects.filter(board=board).delete()[0]
                self.stdout.write(
                    self.style.WARNING(f'Deleted {deleted_count} existing positions')
                )

        # Initialize positions (idempotent)
        with transaction.atomic():
            board.initialize_positions()

        # Report results
        total_positions = board.total_tiles
        created_positions = BoardPosition.objects.filter(board=board).count()
        special_pos = board.default_special_positions()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Board initialization complete!'
            )
        )
        self.stdout.write(
            f'  Total board size: {board.size}x{board.size} = {total_positions} positions'
        )
        self.stdout.write(
            f'  Created/existing positions: {created_positions}'
        )
        self.stdout.write(
            f'\n  Special positions:'
        )
        for name, pos in special_pos.items():
            bp = BoardPosition.objects.filter(board=board, position=pos).first()
            if bp:
                tile_name = bp.tile.title if bp.tile else (
                    bp.city.tile.title if bp.city else "Unknown"
                )
                self.stdout.write(
                    f'    Position {pos:3d} ({name:13s}): {tile_name}'
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'    Position {pos:3d} ({name:13s}): NOT SET'
                    )
                )
