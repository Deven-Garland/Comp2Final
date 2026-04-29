"""
embedded_level_game.py - Generic in-panel wrapper for team games.

Loads a game's Level class directly into the arcade panel surface so all team
games can run through the same launcher flow as Ellie.
"""

from __future__ import annotations

import os
import sys

import pygame


_SHARED_GAME_MODULES = (
    "datastructures", "enemy", "level", "patrol_path", "waypoint",
    "tile", "character", "subcharacter", "weapon", "inventory",
    "inventory_ui", "item", "support", "map_loader", "sprite_loader",
    "time_travel", "debug", "network_client", "settings",
)


def _clear_game_modules() -> None:
    for key in tuple(sys.modules.keys()):
        for marker in _SHARED_GAME_MODULES:
            if marker in key:
                del sys.modules[key]
                break


class EmbeddedLevelGame:
    def __init__(self, game_id: str, surface: pygame.Surface, username: str = "player"):
        self.game_id = game_id
        self.surface = surface
        self.username = username
        self.level = None
        self.chat_focused = False
        self.state = "play"
        self._start_level()

    def _start_level(self) -> None:
        game_dir = os.path.join(os.path.dirname(__file__), f"{self.game_id}_game")
        old_path = sys.path.copy()
        sys.path = [game_dir] + [p for p in sys.path if "arcade_project\\games" not in p and "arcade_project/games" not in p]
        _clear_game_modules()

        host = os.environ.get("ARCADE_GAME_HOST", "127.0.0.1")
        port = int(os.environ.get("ARCADE_GAME_PORT", "50072"))

        original_get_surface = pygame.display.get_surface

        def _patched_surface():
            return self.surface

        pygame.display.get_surface = _patched_surface
        try:
            from level import Level
            from subcharacter import get_all_character_classes

            classes = get_all_character_classes()
            selected_class = classes[0] if classes else None
            if selected_class is None:
                raise RuntimeError(f"No character classes found for {self.game_id}")

            self.level = Level(
                self.username,
                selected_class,
                server_host=host,
                server_port=port,
                serializer="json",
            )
            self.level.display_surface = self.surface
            self.level.visible_sprites.display_surface = self.surface
            self.level.visible_sprites.half_width = self.surface.get_width() // 2
            self.level.visible_sprites.half_height = self.surface.get_height() // 2
        finally:
            pygame.display.get_surface = original_get_surface
            sys.path = old_path

    def cleanup(self) -> None:
        if self.level and hasattr(self.level, "network") and self.level.network:
            try:
                self.level.network.disconnect()
            except Exception:
                pass
        self.level = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.level:
            return
        self.level.handle_events([event])
        self.level.handle_time_travel_input([event])
        self.level.handle_enemy_debug_input([event])

    def update(self, dt: float) -> None:
        if not self.level:
            return
        self.level.player.input_enabled = not self.chat_focused
        self.level.player.update()
        for other in self.level.other_players.values():
            other.update()
        if not self.level.is_time_traveling:
            for enemy in tuple(self.level.enemies):
                enemy.enemy_update(self.level.player)
            self.level.enemies.update()
            self.level.player_attack_logic()
        self.level.record_player_state()
        self.level.update_network()

    def draw(self) -> None:
        if not self.level:
            return
        self.surface.fill((0, 0, 0))
        self.level.visible_sprites.custom_draw(self.level.player)
        self.level.draw_names()
        self.level.draw_status()
        self.level.draw_time_travel_ui()
        self.level.draw_enemy_debug()
        if self.level.inventory_ui.active:
            self.level.inventory_ui.draw(self.surface)
