import builtins
import os
import sys
import time
from contextlib import contextmanager

import pygame

GAME_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(GAME_DIR, "..", "..", ".."))
DEPS_GAME_DIR = os.path.join(os.path.dirname(GAME_DIR), "deven_game")
GAME_SERVER_HOST = os.environ.get("ARCADE_GAME_HOST", "127.0.0.1")
GAME_SERVER_PORT = int(os.environ.get("ARCADE_GAME_PORT", "50072"))

_GAME_MODULES = (
    "datastructures", "enemy", "level", "patrol_path", "waypoint",
    "tile", "character", "subcharacter", "weapon", "inventory",
    "inventory_ui", "item", "support", "map_loader", "sprite_loader",
    "time_travel", "debug", "network_client", "settings",
)


def _clear_game_modules():
    for key in tuple(sys.modules.keys()):
        for marker in _GAME_MODULES:
            if marker in key:
                del sys.modules[key]
                break


def _build_game_sys_path():
    return [GAME_DIR, DEPS_GAME_DIR] + [p for p in sys.path if "arcade_project\\games" not in p and "arcade_project/games" not in p]


class VrajGame:
    def __init__(self, surface: pygame.Surface, username: str = "player"):
        self.surface = surface
        self.username = username
        self.level = None
        self.chat_focused = False
        self.state = "select"
        self.leave_reason = None
        self._leave_btn = None
        self._play_btn = None
        self.selected_idx = 0
        self.character_classes = tuple()
        self._start_time = None
        self._session_stats = {}
        self._network_channel = None
        self._title_font = pygame.font.Font(None, 34)
        self._body_font = pygame.font.Font(None, 22)
        self._small_font = pygame.font.Font(None, 18)
        self._setup_character_select()

    def _resolve_path(self, raw_path: str):
        if not isinstance(raw_path, str) or not raw_path:
            return raw_path
        if os.path.isabs(raw_path):
            return raw_path
        norm = raw_path.replace("\\", "/")
        candidates = (
            os.path.join(GAME_DIR, raw_path),
            os.path.join(REPO_ROOT, raw_path),
            os.path.join(REPO_ROOT, "arcade_project", raw_path),
        )
        if "graphics/" in norm:
            suffix = norm.split("graphics/", 1)[1]
            candidates = candidates + (
                os.path.join(GAME_DIR, "graphics", suffix),
                os.path.join(REPO_ROOT, "arcade_project", "graphics", suffix),
            )
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return raw_path

    @contextmanager
    def _asset_context(self):
        original_image_load = pygame.image.load
        original_open = builtins.open
        original_exists = os.path.exists
        original_isdir = os.path.isdir
        original_isfile = os.path.isfile
        original_listdir = os.listdir
        original_walk = os.walk
        original_abspath = os.path.abspath

        def _resolve(path_like):
            return self._resolve_path(path_like) if isinstance(path_like, str) else path_like

        pygame.image.load = lambda path, *a, **k: original_image_load(_resolve(path), *a, **k)
        builtins.open = lambda file, *a, **k: original_open(_resolve(file), *a, **k)
        os.path.exists = lambda path: original_exists(_resolve(path))
        os.path.isdir = lambda path: original_isdir(_resolve(path))
        os.path.isfile = lambda path: original_isfile(_resolve(path))
        os.listdir = lambda path: original_listdir(_resolve(path))
        os.walk = lambda top, *a, **k: original_walk(_resolve(top), *a, **k)
        os.path.abspath = lambda path: original_abspath(_resolve(path))
        try:
            yield
        finally:
            pygame.image.load = original_image_load
            builtins.open = original_open
            os.path.exists = original_exists
            os.path.isdir = original_isdir
            os.path.isfile = original_isfile
            os.listdir = original_listdir
            os.walk = original_walk
            os.path.abspath = original_abspath

    def _setup_character_select(self):
        old_path = sys.path.copy()
        sys.path = _build_game_sys_path()
        _clear_game_modules()
        try:
            with self._asset_context():
                from subcharacter import get_all_character_classes
                self.character_classes = tuple(get_all_character_classes())
        finally:
            sys.path = old_path

    def _start_level(self):
        old_path = sys.path.copy()
        sys.path = _build_game_sys_path()
        _clear_game_modules()
        original_get_surface = pygame.display.get_surface
        pygame.display.get_surface = lambda: self.surface
        try:
            with self._asset_context():
                from level import Level
                cls = self.character_classes[self.selected_idx] if self.character_classes else None
                self.level = Level(self.username, cls, server_host=GAME_SERVER_HOST, server_port=GAME_SERVER_PORT, serializer="json")
                if self._network_channel and hasattr(self.level, "network") and self.level.network:
                    self.level.network.game_id = self._network_channel
                self.level.display_surface = self.surface
                self.level.visible_sprites.display_surface = self.surface
                self.level.visible_sprites.half_width = self.surface.get_width() // 2
                self.level.visible_sprites.half_height = self.surface.get_height() // 2
                self._start_time = time.time()
                self.state = "play"
        finally:
            pygame.display.get_surface = original_get_surface
            sys.path = old_path

    def set_network_channel(self, chat_channel: str):
        self._network_channel = str(chat_channel) if chat_channel else None
        if self.level and hasattr(self.level, "network") and self.level.network and self._network_channel:
            self.level.network.game_id = self._network_channel

    def cleanup(self):
        if self.level and hasattr(self.level, "network") and self.level.network:
            try:
                self.level.network.disconnect()
            except Exception:
                pass
        self.level = None

    def handle_event(self, event: pygame.event.Event):
        if self.state == "select":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.selected_idx = (self.selected_idx - 1) % len(self.character_classes)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.selected_idx = (self.selected_idx + 1) % len(self.character_classes)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._start_level()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._check_card_click(event.pos)
                if self._play_btn and self._play_btn.collidepoint(event.pos):
                    self._start_level()
            return
        if self.state == "stats":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                w, h = self.surface.get_size()
                back_btn = pygame.Rect(w // 2 - 80, h - 70, 160, 44)
                if back_btn.collidepoint(event.pos):
                    self.state = "done"
            return
        if not self.level:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self._leave_btn and self._leave_btn.collidepoint(event.pos):
            self.leave_reason = "disconnect"
            self._collect_stats()
            self.cleanup()
            self.state = "stats"
            return
        self.level.handle_events([event])
        self.level.handle_time_travel_input([event])
        self.level.handle_enemy_debug_input([event])

    def update(self, dt: float):
        if self.state != "play" or not self.level:
            return
        if getattr(self.level.player, "hp", 1) <= 0:
            self.leave_reason = "death"
            self.cleanup()
            self.state = "done"
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

    def draw(self):
        if self.state == "select":
            self._draw_select()
            return
        if self.state == "stats":
            self._draw_stats()
            return
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
        self._leave_btn = pygame.Rect(self.surface.get_width() - 96, 8, 88, 30)
        pygame.draw.rect(self.surface, (180, 60, 60), self._leave_btn, border_radius=6)
        label = pygame.font.Font(None, 18).render("Leave Game", True, (240, 240, 245))
        self.surface.blit(label, label.get_rect(center=self._leave_btn.center))

    def _check_card_click(self, pos):
        w, h = self.surface.get_size()
        n = len(self.character_classes)
        card_w, card_h = 130, 165
        spacing = 16
        total = n * card_w + (n - 1) * spacing
        x0 = max(10, (w - total) // 2)
        y0 = h // 2 - card_h // 2
        for i in range(n):
            rx = x0 + i * (card_w + spacing)
            if pygame.Rect(rx, y0, card_w, card_h).collidepoint(pos):
                self.selected_idx = i
                return

    def _draw_select(self):
        w, h = self.surface.get_size()
        self.surface.fill((18, 18, 28))
        title_font = pygame.font.Font(None, 34)
        body_font = pygame.font.Font(None, 21)
        self.surface.blit(title_font.render("Choose Your Character", True, (94, 234, 212)), (20, 20))

        n = len(self.character_classes)
        card_w, card_h = 130, 165
        spacing = 16
        total = n * card_w + (n - 1) * spacing
        x0 = max(10, (w - total) // 2)
        y0 = h // 2 - card_h // 2
        for i, cls in enumerate(self.character_classes):
            rx = x0 + i * (card_w + spacing)
            rr = pygame.Rect(rx, y0, card_w, card_h)
            pygame.draw.rect(self.surface, (30, 34, 50), rr, border_radius=10)
            pygame.draw.rect(self.surface, (94, 234, 212) if i == self.selected_idx else (76, 76, 100), rr, 2, border_radius=10)
            image = getattr(cls, "_preview_surface_cached", None)
            if image is None:
                try:
                    with self._asset_context():
                        image = pygame.image.load(cls.get_preview_image()).convert_alpha()
                        image = pygame.transform.smoothscale(image, (68, 68))
                except Exception:
                    image = None
                setattr(cls, "_preview_surface_cached", image)
            if image is not None:
                self.surface.blit(image, image.get_rect(center=(rr.centerx, rr.y + 42)))
            name = cls.get_display_name() if hasattr(cls, "get_display_name") else cls.__name__
            text = body_font.render(name, True, (240, 240, 245))
            self.surface.blit(text, text.get_rect(center=(rr.centerx, rr.y + 96)))

        self._play_btn = pygame.Rect(w // 2 - 80, h - 62, 160, 42)
        pygame.draw.rect(self.surface, (60, 160, 145), self._play_btn, border_radius=8)
        play = body_font.render("Play", True, (240, 240, 245))
        self.surface.blit(play, play.get_rect(center=self._play_btn.center))

    def _collect_stats(self):
        if not self.level:
            return
        elapsed = int(time.time() - self._start_time) if self._start_time else 0
        self._session_stats = {
            "hp": int(getattr(self.level.player, "hp", 0)),
            "max_hp": int(getattr(self.level.player, "max_hp", 0)),
            "xp": int(getattr(self.level.player, "exp", 0)),
            "weapon": (
                self.level.player.equipped_weapon.name
                if getattr(self.level.player, "equipped_weapon", None)
                else "None"
            ),
            "time": elapsed,
            "character": str(getattr(self.level.player, "character_name", "Unknown")).title(),
        }

    def _draw_stats(self):
        w, h = self.surface.get_size()
        self.surface.fill((18, 18, 28))
        title = self._title_font.render("Session Summary", True, (94, 234, 212))
        self.surface.blit(title, title.get_rect(center=(w // 2, 50)))

        s = self._session_stats
        mins = int(s.get("time", 0)) // 60
        secs = int(s.get("time", 0)) % 60
        items = (
            ("Character", s.get("character", "?")),
            ("HP Remaining", f"{s.get('hp', 0)} / {s.get('max_hp', 0)}"),
            ("XP Earned", str(s.get("xp", 0))),
            ("Weapon", s.get("weapon", "None")),
            ("Time Played", f"{mins}m {secs}s"),
        )
        gap = 12
        card_h = 70
        card_w = w - 40
        y0 = 110
        for i, (label, value) in enumerate(items):
            y = y0 + i * (card_h + gap)
            rr = pygame.Rect(20, y, card_w, card_h)
            pygame.draw.rect(self.surface, (28, 28, 42), rr, border_radius=10)
            pygame.draw.rect(self.surface, (70, 70, 95), rr, 1, border_radius=10)
            lab = self._small_font.render(str(label).upper(), True, (160, 160, 180))
            self.surface.blit(lab, (rr.x + 14, rr.y + 12))
            val = self._body_font.render(str(value), True, (240, 240, 245))
            self.surface.blit(val, (rr.x + 14, rr.y + 36))

        back_btn = pygame.Rect(w // 2 - 80, h - 70, 160, 44)
        pygame.draw.rect(self.surface, (60, 160, 145), back_btn, border_radius=8)
        bt = self._body_font.render("Back to Games", True, (240, 240, 245))
        self.surface.blit(bt, bt.get_rect(center=back_btn.center))
