"""
game.py - Ellie's Game integrated into the MOSFET Arcade

Runs the game Level directly inside the arcade window's left panel,
next to the chat. Connects to the C++ game server for multiplayer.

Author: Ellie Lutz
Date: Spring 2026
Lab: Final Project
"""

import os
import sys

# Make sure ellie_game's folder is first in the path
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
if GAME_DIR not in sys.path:
    sys.path.insert(0, GAME_DIR)

import pygame

# C++ game server settings (override for remote ece: ARCADE_GAME_HOST / ARCADE_GAME_PORT)
GAME_SERVER_HOST = os.environ.get("ARCADE_GAME_HOST", "127.0.0.1")
GAME_SERVER_PORT = int(os.environ.get("ARCADE_GAME_PORT", "50072"))

# Modules belonging to ellie_game that need fresh imports
_ELLIE_MODULES = [
    'datastructures', 'enemy', 'level', 'patrol_path', 'waypoint',
    'tile', 'character', 'subcharacter', 'weapon', 'inventory',
    'inventory_ui', 'item', 'support', 'map_loader', 'sprite_loader',
    'time_travel', 'debug', 'network_client', 'settings',
]


def _clear_ellie_modules():
    """Remove ellie_game modules from cache so they reload from GAME_DIR."""
    for key in list(sys.modules.keys()):
        if any(m in key for m in _ELLIE_MODULES):
            del sys.modules[key]


class EllieGame:
    """
    Wraps Level so it draws into a subsurface instead of the full display.
    The arcade passes in the subsurface (left panel) and events each frame.
    """

    def __init__(self, surface: pygame.Surface, username: str = "player"):
        self.surface = surface
        self.username = username
        self.level = None
        self.running = True
        self._setup_character_select()

    def _setup_character_select(self):
        """Build a simple character selection UI."""
        old_path = sys.path.copy()
        sys.path = [GAME_DIR] + [p for p in sys.path if 'arcade_project' not in p]
        _clear_ellie_modules()
        try:
            from subcharacter import get_all_character_classes
            self.character_classes = get_all_character_classes()
        finally:
            sys.path = old_path

        self.selected_idx = 0
        self.state = "select"

        try:
            self.title_font = pygame.font.SysFont("Segoe UI", 28, bold=True)
            self.body_font  = pygame.font.SysFont("Segoe UI", 18)
            self.small_font = pygame.font.SysFont("Segoe UI", 14)
        except Exception:
            self.title_font = pygame.font.Font(None, 32)
            self.body_font  = pygame.font.Font(None, 22)
            self.small_font = pygame.font.Font(None, 18)

    def _start_level(self):
        """Create the Level, connecting to the real C++ game server."""
        old_path = sys.path.copy()
        sys.path = [GAME_DIR] + [p for p in sys.path if 'arcade_project' not in p]
        _clear_ellie_modules()

        _orig = pygame.display.get_surface
        outer_self = self

        def _patched():
            return outer_self.surface

        pygame.display.get_surface = _patched

        try:
            from level import Level
            char_class = self.character_classes[self.selected_idx]
            self.level = Level(
                self.username,
                char_class,
                server_host=GAME_SERVER_HOST,
                server_port=GAME_SERVER_PORT,
                serializer="text",
            )
            self.level.display_surface = self.surface
            self.level.visible_sprites.display_surface = self.surface
            self.level.visible_sprites.half_width  = self.surface.get_width()  // 2
            self.level.visible_sprites.half_height = self.surface.get_height() // 2
        finally:
            pygame.display.get_surface = _orig
            sys.path = old_path

        self.state = "play"

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.state == "select":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.selected_idx = (self.selected_idx - 1) % len(self.character_classes)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.selected_idx = (self.selected_idx + 1) % len(self.character_classes)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._start_level()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                w, h = self.surface.get_size()
                btn = pygame.Rect(w // 2 - 80, h - 70, 160, 44)
                if btn.collidepoint(event.pos):
                    self._start_level()
                self._check_card_click(event.pos)

        elif self.state == "play" and self.level:
            self.level.handle_events([event])
            self.level.handle_time_travel_input([event])
            self.level.handle_enemy_debug_input([event])

    def _check_card_click(self, pos):
        w, h = self.surface.get_size()
        n = len(self.character_classes)
        card_w, card_h = 120, 160
        spacing = 20
        total = n * card_w + (n - 1) * spacing
        x0 = (w - total) // 2
        y0 = h // 2 - card_h // 2 - 20
        for i in range(n):
            rx = x0 + i * (card_w + spacing)
            if pygame.Rect(rx, y0, card_w, card_h).collidepoint(pos):
                self.selected_idx = i
                break

    def update(self, dt: float) -> None:
        if self.state == "play" and self.level:
            self.level.player.update()
            for other in self.level.other_players.values():
                other.update()
            if not self.level.is_time_traveling:
                for enemy in list(self.level.enemies):
                    enemy.enemy_update(self.level.player)
                self.level.enemies.update()
                self.level.player_attack_logic()
            self.level.record_player_state()
            self.level.update_network()

    def draw(self) -> None:
        if self.state == "select":
            self._draw_select()
        elif self.state == "play" and self.level:
            self._draw_play()

    def _draw_select(self):
        w, h = self.surface.get_size()
        self.surface.fill((18, 18, 28))

        title = self.title_font.render("Choose Your Character", True, (94, 234, 212))
        self.surface.blit(title, title.get_rect(center=(w // 2, 40)))

        hint = self.small_font.render("← → to browse  |  Enter to confirm", True, (160, 160, 180))
        self.surface.blit(hint, hint.get_rect(center=(w // 2, 70)))

        n = len(self.character_classes)
        card_w, card_h = 120, 160
        spacing = 20
        total = n * card_w + (n - 1) * spacing
        x0 = (w - total) // 2
        y0 = h // 2 - card_h // 2 - 20

        for i, cls in enumerate(self.character_classes):
            rx = x0 + i * (card_w + spacing)
            selected = (i == self.selected_idx)
            bg = (55, 55, 85) if selected else (28, 28, 42)
            border = (94, 234, 212) if selected else (70, 70, 95)
            pygame.draw.rect(self.surface, bg, (rx, y0, card_w, card_h), border_radius=10)
            pygame.draw.rect(self.surface, border, (rx, y0, card_w, card_h), 2, border_radius=10)

            try:
                img = pygame.image.load(cls.get_preview_image()).convert_alpha()
                img = pygame.transform.scale(img, (64, 64))
                self.surface.blit(img, (rx + card_w // 2 - 32, y0 + 12))
            except Exception:
                pygame.draw.rect(self.surface, (80, 80, 120), (rx + 28, y0 + 12, 64, 64), border_radius=6)

            name = self.body_font.render(cls.get_display_name(), True, (240, 240, 245))
            self.surface.blit(name, name.get_rect(center=(rx + card_w // 2, y0 + 92)))

            desc = cls.get_description()
            words = desc.split()
            lines, line = [], []
            for word in words:
                line.append(word)
                if self.small_font.size(" ".join(line))[0] > card_w - 12:
                    line.pop()
                    lines.append(" ".join(line))
                    line = [word]
            if line:
                lines.append(" ".join(line))
            for j, ln in enumerate(lines[:3]):
                t = self.small_font.render(ln, True, (160, 160, 180))
                self.surface.blit(t, t.get_rect(center=(rx + card_w // 2, y0 + 112 + j * 16)))

        btn = pygame.Rect(w // 2 - 80, h - 70, 160, 44)
        pygame.draw.rect(self.surface, (60, 160, 145), btn, border_radius=8)
        ct = self.body_font.render("Play", True, (240, 240, 245))
        self.surface.blit(ct, ct.get_rect(center=btn.center))

    def _draw_play(self):
        self.surface.fill((0, 0, 0))
        self.level.visible_sprites.custom_draw(self.level.player)
        self.level.draw_names()
        self.level.draw_status()
        self.level.draw_time_travel_ui()
        self.level.draw_enemy_debug()
        if self.level.inventory_ui.active:
            self.level.inventory_ui.draw(self.surface)