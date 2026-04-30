"""
UI screens for the arcade client (pygame).

Screens: Login, Game Browser, Stats, GameStats, Match Queue, Play Session (game area + chat).

Wire callbacks from arcade_client / connection layer; this module only handles
drawing and input.
"""

from __future__ import annotations

import math
from pathlib import Path
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List, Optional, Tuple

import pygame
from datastructures.array import ArrayList
from datastructures.hash_table import HashTable


# --- Theme -----------------------------------------------------------------

def _make_theme_colors():
    colors = HashTable()
    for key, value in (
        ("bg", (18, 18, 28)),
        ("panel", (28, 28, 42)),
        ("panel_light", (38, 38, 58)),
        ("accent", (94, 234, 212)),
        ("accent_dim", (60, 160, 145)),
        ("text", (240, 240, 245)),
        ("text_dim", (160, 160, 180)),
        ("error", (255, 120, 120)),
        ("success", (120, 220, 160)),
        ("border", (70, 70, 95)),
        ("input_bg", (22, 22, 35)),
        ("row_hover", (45, 45, 68)),
        ("row_sel", (55, 55, 85)),
        ("star", (255, 210, 60)),
    ):
        colors[key] = value
    return colors


COLORS = _make_theme_colors()


def _fonts() -> Tuple[pygame.font.Font, pygame.font.Font, pygame.font.Font]:
    pygame.font.init()
    try:
        title = pygame.font.SysFont("Segoe UI", 44, bold=True)
        body = pygame.font.SysFont("Segoe UI", 20)
        small = pygame.font.SysFont("Segoe UI", 16)
    except Exception:
        title = pygame.font.Font(None, 48)
        body = pygame.font.Font(None, 24)
        small = pygame.font.Font(None, 20)
    return title, body, small


TITLE_FONT, BODY_FONT, SMALL_FONT = _fonts()


# --- Small UI primitives ---------------------------------------------------


@dataclass
class Button:
    rect: pygame.Rect
    label: str
    callback: Optional[Callable[[], None]] = None
    enabled: bool = True

    def draw(self, surface: pygame.Surface, hover: bool) -> None:
        bg = COLORS["accent_dim"] if hover and self.enabled else COLORS["panel_light"]
        if not self.enabled:
            bg = (50, 50, 65)
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLORS["border"], self.rect, 1, border_radius=8)
        text = BODY_FONT.render(self.label, True, COLORS["text"] if self.enabled else COLORS["text_dim"])
        tr = text.get_rect(center=self.rect.center)
        surface.blit(text, tr)

    def contains(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


class TextInput:
    """Single-line text field with focus and placeholder."""

    def __init__(self, rect: pygame.Rect, placeholder: str = "", password: bool = False):
        self.rect = rect
        self.placeholder = placeholder
        self.text = ""
        self.focused = False
        self.password = password
        self._cursor_blink = 0.0
        self.focus_region: Optional[pygame.Rect] = None

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLORS["input_bg"], self.rect, border_radius=6)
        border = COLORS["accent"] if self.focused else COLORS["border"]
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=6)
        display = ("*" * len(self.text)) if self.password else self.text
        if not display and not self.focused:
            t = SMALL_FONT.render(self.placeholder, True, COLORS["text_dim"])
        else:
            t = BODY_FONT.render(display + ("|" if self.focused and (int(self._cursor_blink * 2) % 2) else ""), True, COLORS["text"])
        surface.blit(t, (self.rect.x + 10, self.rect.centery - t.get_height() // 2))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked_input = self.rect.collidepoint(event.pos)
            in_region = (
                self.focus_region is None or
                self.focus_region.collidepoint(event.pos)
            )
            if clicked_input:
                self.focused = True
            elif in_region:
                self.focused = False
            return clicked_input
        if not self.focused:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            if event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
                return False
            if event.unicode and event.unicode.isprintable() and len(self.text) < 128:
                self.text += event.unicode
                return True
        return False

    def tick(self, dt: float) -> None:
        if self.focused:
            self._cursor_blink = (self._cursor_blink + dt) % 1.0


# --- Login -----------------------------------------------------------------


class LoginScreen:
    def __init__(
        self,
        rect: pygame.Rect,
        on_login: Callable[[str, str], None],
        on_register: Callable[[str, str], None],
    ):
        self.rect = rect
        self.on_login = on_login
        self.on_register = on_register
        self.status = ""
        self.status_is_error = False
        margin = 40
        w = min(400, rect.width - 2 * margin)
        cx = rect.centerx
        y0 = rect.centery - 120
        self._user = TextInput(pygame.Rect(cx - w // 2, y0, w, 40), "Username")
        self._pass = TextInput(pygame.Rect(cx - w // 2, y0 + 52, w, 40), "Password", password=True)
        self._btn_login = Button(pygame.Rect(cx - w // 2, y0 + 110, w // 2 - 6, 44), "Log in")
        self._btn_reg = Button(pygame.Rect(cx + 6, y0 + 110, w // 2 - 6, 44), "Register")

    def set_status(self, message: str, error: bool = False) -> None:
        self.status = message
        self.status_is_error = error

    def handle_event(self, event: pygame.event.Event) -> None:
        self._user.handle_event(event)
        self._pass.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._btn_login.contains(event.pos):
                self.on_login(self._user.text.strip(), self._pass.text)
            elif self._btn_reg.contains(event.pos):
                self.on_register(self._user.text.strip(), self._pass.text)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            if self._user.focused:
                self._user.focused = False
                self._pass.focused = True
            elif self._pass.focused:
                self._pass.focused = False
                self._user.focused = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.on_login(self._user.text.strip(), self._pass.text)

    def update(self, dt: float) -> None:
        self._user.tick(dt)
        self._pass.tick(dt)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLORS["bg"], self.rect)
        title = TITLE_FONT.render("MOSFET Arcade", True, COLORS["accent"])
        surface.blit(title, title.get_rect(center=(self.rect.centerx, self.rect.centery - 200)))
        sub = SMALL_FONT.render("Sign in or create an account", True, COLORS["text_dim"])
        surface.blit(sub, sub.get_rect(center=(self.rect.centerx, self.rect.centery - 155)))
        self._user.draw(surface)
        self._pass.draw(surface)
        mp = pygame.mouse.get_pos()
        self._btn_login.draw(surface, self._btn_login.contains(mp))
        self._btn_reg.draw(surface, self._btn_reg.contains(mp))
        if self.status:
            c = COLORS["error"] if self.status_is_error else COLORS["success"]
            st = SMALL_FONT.render(self.status, True, c)
            surface.blit(st, st.get_rect(center=(self.rect.centerx, self.rect.centery - 30)))


# --- Game browser ----------------------------------------------------------


@dataclass
class GameInfo:
    id: str
    name: str
    description: str = ""


class BrowserScreen:
    def __init__(
        self,
        rect: pygame.Rect,
        on_play: Callable[[str], None],
        on_logout: Callable[[], None],
        on_stats: Callable[[], None],
        on_leaderboard: Callable[[], None],
        on_star: Optional[Callable[[str], None]] = None,
        on_rate: Optional[Callable[[str, int], bool]] = None,
        on_search_players: Optional[Callable[[str], List[dict]]] = None,
        on_select_player: Optional[Callable[[str], Optional[dict]]] = None,
        on_game_stats: Optional[Callable[[str], None]] = None,
        games: Optional[List[GameInfo]] = None,
    ):
        self.rect = rect
        self.on_play = on_play
        self.on_logout = on_logout
        self.on_stats = on_stats
        self.on_leaderboard = on_leaderboard
        self.on_star = on_star
        self.on_rate = on_rate
        self.on_search_players = on_search_players
        self.on_select_player = on_select_player
        self.on_game_stats = on_game_stats
        self.favorite_game_id = ""
        self.game_ratings = HashTable()
        self.user_ratings = HashTable()
        self.games = ArrayList()
        default_games = (
            GameInfo("deven",    "Where the Fog Remembers", "Horror/adventure · explore & chat"),
            GameInfo("ellie",    "Eli's Legacy",            "Fantasy/adventure · compete for high score"),
            GameInfo("kimberly", "Fate of the Fists",       "Adventure/combat · fight to win"),
            GameInfo("mennah",   "Doom in Delta",           "Historical RPG · complete secret missions"),
            GameInfo("vraj",     "Echoes of the Iron Realm","Top-down action RPG · real-time multiplayer"),
        )
        for game in games or default_games:
            self.games.append(game)
        self._star_icon = None
        self._load_star_icon()
        self._selected: Optional[int] = None
        self._scroll = 0
        self._hover_row = -1
        self._last_search_text = ""
        self._search_results = ArrayList()
        self._selected_profile: Optional[dict] = None
        pad = 24
        self._search_input = TextInput(
            pygame.Rect(rect.right - pad - 280, rect.y + 66, 280, 32),
            "Search players...",
        )
        self._list_rect = pygame.Rect(rect.x + pad, rect.y + 106, rect.width - 2 * pad, rect.height - 206)
        self._btn_stats = Button(pygame.Rect(rect.right - pad - 260, rect.y + 24, 120, 36), "View stats")
        self._btn_lb = Button(pygame.Rect(rect.right - pad - 130, rect.y + 24, 120, 36), "Leaderboard")
        self._btn_play = Button(pygame.Rect(rect.right - pad - 160, rect.bottom - 72, 150, 44), "Find match")
        self._btn_out = Button(pygame.Rect(rect.x + pad, rect.bottom - 72, 120, 44), "Log out")
        # "My Stats" button shown when a game row is selected, bottom-center
        self._btn_game_stats = Button(
            pygame.Rect(rect.centerx - 75, rect.bottom - 72, 150, 44), "My Stats"
        )

    def _search_results_rect(self) -> pygame.Rect:
        rows = min(6, len(self._search_results))
        return pygame.Rect(
            self._search_input.rect.x,
            self._search_input.rect.bottom + 4,
            self._search_input.rect.width,
            max(0, rows * 26),
        )

    def set_games(self, games: List[GameInfo]) -> None:
        self.games = ArrayList()
        for game in games:
            self.games.append(game)
        self._selected = None
        self._scroll = 0

    def set_favorite(self, game_id: str) -> None:
        self.favorite_game_id = game_id

    def set_ratings(self, ratings) -> None:
        self.game_ratings = HashTable()
        if not ratings:
            return
        for game_id in ratings:
            self.game_ratings[game_id] = float(ratings[game_id])

    def set_user_rating(self, game_id: str, stars: int) -> None:
        self.user_ratings[game_id] = max(1, min(5, int(stars)))

    def _load_star_icon(self) -> None:
        root = Path(__file__).resolve().parents[2]
        candidates = (
            root / "arcade_project" / "Graphic" / "star.png",
            root / "assets" / "star_rating.png",
        )
        for candidate in candidates:
            if not candidate.exists():
                continue
            try:
                self._star_icon = pygame.image.load(str(candidate)).convert_alpha()
                self._star_icon = pygame.transform.smoothscale(self._star_icon, (16, 16))
                return
            except Exception:
                self._star_icon = None

    def _star_rect_for_row(self, rr: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(rr.right - 36, rr.centery - 14, 28, 28)

    def _rating_rect_for_row(self, rr: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(rr.right - 116, rr.centery - 10, 74, 20)

    def _rating_click_rect_for_row(self, rr: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(rr.right - 228, rr.centery - 10, 106, 20)

    def handle_event(self, event: pygame.event.Event) -> None:
        self._search_input.handle_event(event)

        if event.type == pygame.KEYDOWN and self._search_input.focused:
            query = self._search_input.text.strip()
            if query != self._last_search_text:
                self._last_search_text = query
                if self.on_search_players and query:
                    self._search_results = ArrayList()
                    raw_results = self.on_search_players(query)
                    max_items = min(6, len(raw_results))
                    for i in range(max_items):
                        self._search_results.append(raw_results[i])
                else:
                    self._search_results = ArrayList()
            if event.key == pygame.K_RETURN and self._search_results:
                first = self._search_results[0]
                username = first.get("name") or first.get("username")
                if username and self.on_select_player:
                    self._selected_profile = self.on_select_player(username)
                    self._search_input.text = username
                    self._search_results = ArrayList()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            result_box = self._search_results_rect()
            if result_box.collidepoint(event.pos) and self._search_results:
                rel_y = event.pos[1] - result_box.y
                idx = rel_y // 26
                if 0 <= idx < len(self._search_results):
                    row = self._search_results[idx]
                    username = row.get("name") or row.get("username")
                    if username and self.on_select_player:
                        self._selected_profile = self.on_select_player(username)
                        self._search_input.text = username
                        self._search_results = ArrayList()
                        return

            if self._btn_stats.contains(event.pos):
                self.on_stats()
            elif self._btn_lb.contains(event.pos):
                self.on_leaderboard()
            elif self._btn_play.contains(event.pos) and self._selected is not None:
                gid = self.games[self._selected].id
                self.on_play(gid)
            elif self._btn_out.contains(event.pos):
                self.on_logout()
            elif (
                self._btn_game_stats.contains(event.pos)
                and self._selected is not None
                and self.on_game_stats
            ):
                gid = self.games[self._selected].id
                self.on_game_stats(gid)
            elif self._list_rect.collidepoint(event.pos):
                row_h = 56
                y = event.pos[1] - self._list_rect.y + self._scroll
                idx = y // row_h
                if 0 <= idx < len(self.games):
                    ry = self._list_rect.y - self._scroll + idx * row_h
                    rr = pygame.Rect(self._list_rect.x + 4, ry + 4, self._list_rect.width - 8, row_h - 8)
                    gid = self.games[idx].id
                    rating_click_rect = self._rating_click_rect_for_row(rr)
                    if rating_click_rect.collidepoint(event.pos) and self.on_rate:
                        relative_x = event.pos[0] - rating_click_rect.x
                        stars = max(1, min(5, int(relative_x // 20) + 1))
                        result = self.on_rate(gid, stars)
                        if result is not False:
                            self.set_user_rating(gid, stars)
                        return
                    star_rect = self._star_rect_for_row(rr)
                    if star_rect.collidepoint(event.pos) and self.on_star:
                        if self.favorite_game_id == gid:
                            self.favorite_game_id = ""
                            self.on_star("")
                        else:
                            self.favorite_game_id = gid
                            self.on_star(gid)
                    else:
                        self._selected = idx
        elif event.type == pygame.KEYDOWN and self._selected is not None and self.on_rate and not self._search_input.focused:
            stars = None
            if pygame.K_1 <= event.key <= pygame.K_5:
                stars = event.key - pygame.K_0
            elif pygame.K_KP1 <= event.key <= pygame.K_KP5:
                stars = event.key - pygame.K_KP0
            if stars is not None:
                gid = self.games[self._selected].id
                result = self.on_rate(gid, stars)
                if result is not False:
                    self.set_user_rating(gid, stars)
        elif event.type == pygame.MOUSEWHEEL:
            self._scroll = max(0, self._scroll - event.y * 24)
        elif event.type == pygame.MOUSEMOTION:
            if self._list_rect.collidepoint(event.pos):
                row_h = 56
                y = event.pos[1] - self._list_rect.y + self._scroll
                self._hover_row = y // row_h if 0 <= y // row_h < len(self.games) else -1
            else:
                self._hover_row = -1

    def update(self, dt: float) -> None:
        max_scroll = max(0, len(self.games) * 56 - self._list_rect.height)
        self._scroll = min(self._scroll, max_scroll)
        self._search_input.tick(dt)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLORS["bg"], self.rect)
        t = TITLE_FONT.render("Games", True, COLORS["text"])
        surface.blit(t, (self.rect.x + 24, self.rect.y + 24))
        sub = SMALL_FONT.render("Select a title, then find a match. Star + number is average rating. Circle toggles favorite.", True, COLORS["text_dim"])
        surface.blit(sub, (self.rect.x + 24, self.rect.y + 72))
        self._search_input.draw(surface)

        result_box = self._search_results_rect()
        if self._search_results and self._search_input.text.strip():
            pygame.draw.rect(surface, COLORS["panel"], result_box, border_radius=6)
            pygame.draw.rect(surface, COLORS["border"], result_box, 1, border_radius=6)
            for i, row in enumerate(self._search_results):
                y = result_box.y + i * 26
                rr = pygame.Rect(result_box.x + 2, y + 2, result_box.width - 4, 22)
                if rr.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(surface, COLORS["row_hover"], rr, border_radius=4)
                label = row.get("name") or row.get("username") or "unknown"
                txt = SMALL_FONT.render(str(label), True, COLORS["text"])
                surface.blit(txt, (rr.x + 8, rr.y + 3))

        pygame.draw.rect(surface, COLORS["panel"], self._list_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["border"], self._list_rect, 1, border_radius=10)

        row_h = 56
        clip = surface.get_clip()
        surface.set_clip(self._list_rect)
        for i, g in enumerate(self.games):
            ry = self._list_rect.y - self._scroll + i * row_h
            rr = pygame.Rect(self._list_rect.x + 4, ry + 4, self._list_rect.width - 8, row_h - 8)
            if not rr.colliderect(self._list_rect):
                continue
            if i == self._selected:
                pygame.draw.rect(surface, COLORS["row_sel"], rr, border_radius=8)
            elif i == self._hover_row:
                pygame.draw.rect(surface, COLORS["row_hover"], rr, border_radius=8)

            name = BODY_FONT.render(g.name, True, COLORS["text"])
            surface.blit(name, (rr.x + 12, rr.y + 8))
            desc = SMALL_FONT.render(g.description[:80], True, COLORS["text_dim"])
            surface.blit(desc, (rr.x + 12, rr.y + 30))

            rating = float(self.game_ratings[g.id]) if g.id in self.game_ratings else 0.0
            rating_rect = self._rating_rect_for_row(rr)
            if self._star_icon is not None:
                surface.blit(self._star_icon, (rating_rect.x, rating_rect.y + 2))
            else:
                points = ArrayList()
                cx, cy = rating_rect.x + 8, rating_rect.y + 10
                for n in range(10):
                    ang = math.radians(-90 + n * 36)
                    rad = 7 if n % 2 == 0 else 3
                    points.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
                pygame.draw.polygon(surface, COLORS["star"], points)
            rt = SMALL_FONT.render(f"{rating:.1f}", True, COLORS["text"])
            surface.blit(rt, (rating_rect.x + 20, rating_rect.y + 1))

            selected = int(self.user_ratings[g.id]) if g.id in self.user_ratings else 0
            rating_click_rect = self._rating_click_rect_for_row(rr)
            for star_idx in range(1, 6):
                sx = rating_click_rect.x + (star_idx - 1) * 20 + 8
                sy = rating_click_rect.y + 10
                points = ArrayList()
                for n in range(10):
                    ang = math.radians(-90 + n * 36)
                    rad = 7 if n % 2 == 0 else 3
                    points.append((sx + math.cos(ang) * rad, sy + math.sin(ang) * rad))
                if star_idx <= selected:
                    pygame.draw.polygon(surface, COLORS["star"], points)
                else:
                    pygame.draw.polygon(surface, COLORS["border"], points, 1)

            star_rect = self._star_rect_for_row(rr)
            is_fav = self.favorite_game_id == g.id
            cx = star_rect.centerx
            cy = star_rect.centery
            r = 10
            if is_fav:
                pygame.draw.circle(surface, COLORS["star"], (cx, cy), r)
                pygame.draw.circle(surface, (180, 140, 20), (cx, cy), 4)
            else:
                pygame.draw.circle(surface, COLORS["border"], (cx, cy), r, 2)

        surface.set_clip(clip)

        mp = pygame.mouse.get_pos()
        self._btn_stats.draw(surface, self._btn_stats.contains(mp))
        self._btn_lb.draw(surface, self._btn_lb.contains(mp))
        self._btn_play.enabled = self._selected is not None
        self._btn_play.draw(surface, self._btn_play.contains(mp))
        self._btn_out.draw(surface, self._btn_out.contains(mp))

        # "My Stats" button only shown when a game is selected
        if self._selected is not None and self.on_game_stats:
            self._btn_game_stats.draw(surface, self._btn_game_stats.contains(mp))

        if self._selected_profile:
            box = pygame.Rect(self.rect.right - 304, self.rect.y + 132, 280, 122)
            pygame.draw.rect(surface, COLORS["panel"], box, border_radius=8)
            pygame.draw.rect(surface, COLORS["border"], box, 1, border_radius=8)
            name = self._selected_profile.get("name", "Player")
            surface.blit(BODY_FONT.render(str(name), True, COLORS["accent"]), (box.x + 10, box.y + 8))
            lines = ArrayList()
            lines.append(f"Minutes: {self._selected_profile.get('total_play_time', 0)}")
            lines.append(f"Messages: {self._selected_profile.get('messages_sent', 0)}")
            lines.append(f"Favorite: {self._selected_profile.get('favorite_game', '') or 'None'}")
            lines.append(f"Games: {self._selected_profile.get('games_played', 0)}")
            for i, line in enumerate(lines):
                surface.blit(SMALL_FONT.render(line, True, COLORS["text"]), (box.x + 10, box.y + 34 + i * 20))


# --- Player stats ----------------------------------------------------------


@dataclass
class PlayerStats:
    """Snapshot for the stats screen (fill from platform server)."""
    games_played: int = 0
    messages_sent: int = 0
    favorite_game: str = "None"
    minutes_played: int = 0


def _format_minutes(minutes: int) -> str:
    if minutes <= 0:
        return "0 min"
    if minutes < 60:
        return f"{minutes} min"
    h = minutes // 60
    m = minutes % 60
    if m == 0:
        return f"{h} h"
    return f"{h} h {m} min"


class StatsScreen:
    """Shows account-wide stats: games, messages, favorite game, time played."""

    def __init__(
        self,
        rect: pygame.Rect,
        on_back: Callable[[], None],
        stats: Optional[PlayerStats] = None,
    ):
        self.rect = rect
        self.on_back = on_back
        self.stats = stats or PlayerStats()
        pad = 24
        self._btn_back = Button(pygame.Rect(rect.x + pad, rect.y + pad, 120, 40), "Back")

    def set_stats(self, stats: PlayerStats) -> None:
        self.stats = stats

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._btn_back.contains(event.pos):
                self.on_back()

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLORS["bg"], self.rect)
        title = TITLE_FONT.render("Your stats", True, COLORS["accent"])
        surface.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 88))
        sub = SMALL_FONT.render("Totals for your account (from the platform server)", True, COLORS["text_dim"])
        surface.blit(sub, sub.get_rect(center=(self.rect.centerx, self.rect.y + 138)))

        items = ArrayList()
        items.append(("Games played", str(self.stats.games_played)))
        items.append(("Messages sent", str(self.stats.messages_sent)))
        items.append(("Favorite game", self.stats.favorite_game or "None"))
        items.append(("Minutes played", _format_minutes(self.stats.minutes_played)))
        gap = 16
        card_w = min(420, (self.rect.width - 48 - gap) // 2)
        card_h = 100
        grid_top = self.rect.y + 180
        pair_w = 2 * card_w + gap
        x0 = self.rect.centerx - pair_w // 2
        for i, (label, value) in enumerate(items):
            col = i % 2
            row = i // 2
            x = x0 + col * (card_w + gap)
            y = grid_top + row * (card_h + gap)
            rr = pygame.Rect(x, y, card_w, card_h)
            pygame.draw.rect(surface, COLORS["panel"], rr, border_radius=12)
            pygame.draw.rect(surface, COLORS["border"], rr, 1, border_radius=12)
            lab = SMALL_FONT.render(label.upper(), True, COLORS["text_dim"])
            surface.blit(lab, (rr.x + 16, rr.y + 14))
            val_font = BODY_FONT if len(value) > 12 else TITLE_FONT
            val = val_font.render(value, True, COLORS["text"])
            surface.blit(val, (rr.x + 16, rr.y + 44))

        mp = pygame.mouse.get_pos()
        self._btn_back.draw(surface, self._btn_back.contains(mp))


# --- Per-game stats screen -------------------------------------------------


class GameStatsScreen:
    """Shows a single player's stats for one specific game."""

    def __init__(self, rect: pygame.Rect, on_back: Callable[[], None]):
        self.rect = rect
        self.on_back = on_back
        self._game_name = ""
        self._stats: HashTable = HashTable()
        # ArrayList of (stat_key, display_label) pairs
        self._stat_labels = ArrayList()
        for pair in (
            ("sessions",    "Sessions Played"),
            ("score",       "Best Score"),
            ("play_time",   "Minutes Played"),
            ("chats",       "Chats Sent"),
            ("deaths",      "Deaths"),
            ("disconnects", "Disconnects"),
        ):
            self._stat_labels.append(pair)
        pad = 24
        self._btn_back = Button(pygame.Rect(rect.x + pad, rect.y + pad, 120, 40), "Back")

    def set_stats(self, game_name: str, stats: HashTable) -> None:
        self._game_name = game_name
        self._stats = stats

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._btn_back.contains(event.pos):
                self.on_back()

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLORS["bg"], self.rect)

        title = TITLE_FONT.render(self._game_name or "Game Stats", True, COLORS["accent"])
        surface.blit(title, title.get_rect(center=(self.rect.centerx, self.rect.y + 70)))
        sub = SMALL_FONT.render("Your personal stats for this game", True, COLORS["text_dim"])
        surface.blit(sub, sub.get_rect(center=(self.rect.centerx, self.rect.y + 115)))

        gap = 16
        cols = 3
        card_w = (self.rect.width - 48 - gap * (cols - 1)) // cols
        card_h = 110
        grid_top = self.rect.y + 148
        total_w = cols * card_w + (cols - 1) * gap
        x0 = self.rect.centerx - total_w // 2

        for i, (stat_key, label) in enumerate(self._stat_labels):
            col = i % cols
            row = i // cols
            x = x0 + col * (card_w + gap)
            y = grid_top + row * (card_h + gap)
            rr = pygame.Rect(x, y, card_w, card_h)
            pygame.draw.rect(surface, COLORS["panel"], rr, border_radius=12)
            pygame.draw.rect(surface, COLORS["border"], rr, 1, border_radius=12)

            lab = SMALL_FONT.render(label.upper(), True, COLORS["text_dim"])
            surface.blit(lab, (rr.x + 14, rr.y + 12))

            entry = self._stats[stat_key] if stat_key in self._stats else None
            rank = entry.get("rank") if entry and hasattr(entry, "get") else None
            value = entry.get("value") if entry and hasattr(entry, "get") else None

            # Show value if we have it, otherwise show rank
            if value is not None:
                main_text = str(value)
                sub_text = f"Rank #{rank}" if rank is not None else ""
            elif rank is not None:
                main_text = f"Rank #{rank}"
                sub_text = ""
            else:
                main_text = "—"
                sub_text = "No data yet"

            val_surf = BODY_FONT.render(main_text, True, COLORS["text"])
            surface.blit(val_surf, (rr.x + 14, rr.y + 42))

            if sub_text:
                sub_surf = SMALL_FONT.render(sub_text, True, COLORS["text_dim"])
                surface.blit(sub_surf, (rr.x + 14, rr.y + 72))

        mp = pygame.mouse.get_pos()
        self._btn_back.draw(surface, self._btn_back.contains(mp))


# --- Leaderboard -----------------------------------------------------------


class LeaderboardScreen:
    def __init__(
        self,
        rect: pygame.Rect,
        on_back: Callable[[], None],
        on_refresh: Callable[[str, str], Tuple[List[str], Optional[int], List[str]]],
        games: Optional[List[GameInfo]] = None,
    ):
        self.rect = rect
        self.on_back = on_back
        self.on_refresh = on_refresh
        self.games = ArrayList()
        for game in games or ():
            self.games.append(game)
        self.game_idx = 0
        self.stats = ArrayList()
        for stat in ("score", "chats", "deaths", "disconnects", "play_time", "sessions"):
            self.stats.append(stat)
        self.stat_idx = 0
        self.top_rows = ArrayList()
        self.range_rows = ArrayList()
        self.rank_value: Optional[int] = None
        self.status = ""

        pad = 24
        self._btn_back = Button(pygame.Rect(rect.x + pad, rect.y + pad, 120, 40), "Back")
        self._btn_game = Button(pygame.Rect(rect.x + pad, rect.y + 84, 220, 36), "Game")
        self._btn_stat = Button(pygame.Rect(rect.x + pad + 236, rect.y + 84, 220, 36), "Stat")
        self._btn_refresh = Button(pygame.Rect(rect.right - pad - 140, rect.y + 84, 140, 36), "Refresh")

    def _current_game(self) -> str:
        if not self.games:
            return "global"
        return self.games[self.game_idx].id

    def _current_stat(self) -> str:
        return self.stats[self.stat_idx]

    def refresh(self) -> None:
        game = self._current_game()
        stat = self._current_stat()
        try:
            top_rows_raw, self.rank_value, range_rows_raw = self.on_refresh(game, stat)
            self.top_rows = ArrayList()
            self.range_rows = ArrayList()
            for row in top_rows_raw:
                self.top_rows.append(row)
            for row in range_rows_raw:
                self.range_rows.append(row)
            self.status = f"Loaded {game}:{stat}"
        except Exception as error:
            self.status = f"Load failed: {error}"
            self.top_rows = ArrayList()
            self.range_rows = ArrayList()
            self.rank_value = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._btn_back.contains(event.pos):
                self.on_back()
            elif self._btn_game.contains(event.pos):
                total = max(1, len(self.games))
                self.game_idx = (self.game_idx + 1) % total
                self.refresh()
            elif self._btn_stat.contains(event.pos):
                self.stat_idx = (self.stat_idx + 1) % len(self.stats)
                self.refresh()
            elif self._btn_refresh.contains(event.pos):
                self.refresh()

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLORS["bg"], self.rect)
        title = TITLE_FONT.render("Leaderboard", True, COLORS["accent"])
        surface.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 24))

        game_label = f"Game: {self._current_game()}"
        stat_label = f"Stat: {self._current_stat()}"
        self._btn_game.label = game_label
        self._btn_stat.label = stat_label

        mp = pygame.mouse.get_pos()
        self._btn_back.draw(surface, self._btn_back.contains(mp))
        self._btn_game.draw(surface, self._btn_game.contains(mp))
        self._btn_stat.draw(surface, self._btn_stat.contains(mp))
        self._btn_refresh.draw(surface, self._btn_refresh.contains(mp))

        rank_text = f"Your rank: {self.rank_value}" if self.rank_value is not None else "Your rank: -"
        rank_render = BODY_FONT.render(rank_text, True, COLORS["text"])
        surface.blit(rank_render, (self.rect.x + 24, self.rect.y + 138))

        status_render = SMALL_FONT.render(self.status, True, COLORS["text_dim"])
        surface.blit(status_render, (self.rect.x + 24, self.rect.y + 168))

        top_box = pygame.Rect(self.rect.x + 24, self.rect.y + 198, self.rect.width // 2 - 36, self.rect.height - 222)
        range_box = pygame.Rect(self.rect.centerx + 12, self.rect.y + 198, self.rect.width // 2 - 36, self.rect.height - 222)
        for box, heading in ((top_box, "Top Players"), (range_box, "Range Query")):
            pygame.draw.rect(surface, COLORS["panel"], box, border_radius=10)
            pygame.draw.rect(surface, COLORS["border"], box, 1, border_radius=10)
            hdr = BODY_FONT.render(heading, True, COLORS["text"])
            surface.blit(hdr, (box.x + 12, box.y + 10))

        y = top_box.y + 44
        top_limit = min(12, len(self.top_rows))
        for i in range(top_limit):
            idx = i + 1
            row = self.top_rows[i]
            line = SMALL_FONT.render(f"{idx}. {row}", True, COLORS["text"])
            surface.blit(line, (top_box.x + 12, y))
            y += 24

        y = range_box.y + 44
        range_limit = min(12, len(self.range_rows))
        for i in range(range_limit):
            row = self.range_rows[i]
            line = SMALL_FONT.render(str(row), True, COLORS["text"])
            surface.blit(line, (range_box.x + 12, y))
            y += 24


# --- Queue / waiting -------------------------------------------------------


class QueueScreen:
    def __init__(self, rect: pygame.Rect, game_name: str, on_cancel: Callable[[], None]):
        self.rect = rect
        self.game_name = game_name
        self.on_cancel = on_cancel
        self.detail = "Talking to matchmaker..."
        self._btn_cancel = Button(pygame.Rect(rect.centerx - 70, rect.centery + 80, 140, 44), "Cancel")

    def set_detail(self, text: str) -> None:
        self.detail = text

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._btn_cancel.contains(event.pos):
                self.on_cancel()

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLORS["bg"], self.rect)
        t = TITLE_FONT.render("Finding match", True, COLORS["accent"])
        surface.blit(t, t.get_rect(center=(self.rect.centerx, self.rect.centery - 40)))
        g = BODY_FONT.render(self.game_name, True, COLORS["text"])
        surface.blit(g, g.get_rect(center=(self.rect.centerx, self.rect.centery + 10)))
        d = SMALL_FONT.render(self.detail, True, COLORS["text_dim"])
        surface.blit(d, d.get_rect(center=(self.rect.centerx, self.rect.centery + 44)))
        t_anim = pygame.time.get_ticks() / 1000.0
        cx, cy = self.rect.centerx, self.rect.centery - 100
        r = 28
        for i in range(8):
            ang = t_anim * 3 + i * (math.tau / 8)
            alpha = 0.3 + 0.7 * (i / 8)
            c = tuple(int(COLORS["accent"][j] * alpha + COLORS["bg"][j] * (1 - alpha)) for j in range(3))
            px = int(cx + math.cos(ang) * r)
            py = int(cy + math.sin(ang) * r)
            pygame.draw.circle(surface, c, (px, py), 4)
        mp = pygame.mouse.get_pos()
        self._btn_cancel.draw(surface, self._btn_cancel.contains(mp))


# --- Play session: game area + chat ----------------------------------------


@dataclass
class ChatLine:
    sender: str
    text: str
    timestamp: float = 0.0


class PlaySessionScreen:
    def __init__(
        self,
        rect: pygame.Rect,
        game_title: str,
        session_id: str,
        on_send_chat: Callable[[str], None],
        on_leave: Callable[[], None],
    ):
        self.rect = rect
        self.game_title = game_title
        self.session_id = session_id
        self.chat_channel = "global"
        self.on_send_chat = on_send_chat
        self.on_leave = on_leave
        self.chat_lines = ArrayList()
        self.connection_count = 0
        self.connection_limit = 30
        self._chat_scroll = 0
        split = int(rect.width * 0.62)
        self._game_rect = pygame.Rect(rect.x, rect.y, split, rect.height)
        self._chat_rect = pygame.Rect(rect.x + split, rect.y, rect.width - split, rect.height)
        pad = 12
        self._history_rect = pygame.Rect(
            self._chat_rect.x + pad,
            self._chat_rect.y + 52,
            self._chat_rect.width - 2 * pad,
            self._chat_rect.height - 120,
        )
        self._input = TextInput(
            pygame.Rect(
                self._chat_rect.x + pad,
                self._chat_rect.bottom - 52,
                self._chat_rect.width - 2 * pad - 88,
                36,
            ),
            "Type a message…",
        )
        self._input.focus_region = self._chat_rect

        self._btn_send = Button(
            pygame.Rect(self._chat_rect.right - pad - 80, self._chat_rect.bottom - 52, 76, 36),
            "Send",
        )
        self._btn_leave = Button(pygame.Rect(rect.x + 16, rect.y + 16, 100, 36), "Leave")

    @property
    def chat_input_focused(self) -> bool:
        return self._input.focused

    def add_chat(self, sender: str, text: str, timestamp: float = 0.0) -> None:
        self.chat_lines.append(ChatLine(sender=sender, text=text, timestamp=timestamp))
        total_h = len(self.chat_lines) * 40 + 8
        self._chat_scroll = max(0, total_h - self._history_rect.height)

    def clear_chat(self) -> None:
        self.chat_lines = ArrayList()
        self._chat_scroll = 0

    def set_connection_status(self, current_players: int, max_players: int) -> None:
        self.connection_count = int(current_players)
        self.connection_limit = int(max_players)

    def set_chat_channel(self, chat_channel: str) -> None:
        self.chat_channel = str(chat_channel) if chat_channel else "global"

    def game_subsurface(self, surface: pygame.Surface) -> pygame.Surface:
        return surface.subsurface(self._game_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        self._input.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._game_rect.collidepoint(event.pos):
                self._input.focused = False
            elif self._btn_send.contains(event.pos):
                self._submit_chat()
            elif self._btn_leave.contains(event.pos):
                self.on_leave()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self._input.focused:
            self._submit_chat()
        if event.type == pygame.MOUSEWHEEL and self._history_rect.collidepoint(pygame.mouse.get_pos()):
            self._chat_scroll = max(0, self._chat_scroll - event.y * 20)

    def _submit_chat(self) -> None:
        t = self._input.text.strip()
        if t:
            self.on_send_chat(t)
            self._input.text = ""

    def update(self, dt: float) -> None:
        self._input.tick(dt)
        max_scroll = max(0, len(self.chat_lines) * 40 + 8 - self._history_rect.height)
        self._chat_scroll = min(self._chat_scroll, max_scroll)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLORS["bg"], self.rect)
        pygame.draw.rect(surface, COLORS["panel"], self._game_rect)
        pygame.draw.line(surface, COLORS["border"], (self._game_rect.right, self._game_rect.y), (self._game_rect.right, self._game_rect.bottom))
        placeholder = BODY_FONT.render(self.game_title, True, COLORS["text_dim"])
        surface.blit(placeholder, placeholder.get_rect(center=self._game_rect.center))
        hint = SMALL_FONT.render("Game renders in this area", True, COLORS["text_dim"])
        surface.blit(hint, hint.get_rect(center=(self._game_rect.centerx, self._game_rect.centery + 28)))

        pygame.draw.rect(surface, COLORS["panel_light"], self._chat_rect)
        ct = BODY_FONT.render("Chat", True, COLORS["accent"])
        surface.blit(ct, (self._chat_rect.x + 12, self._chat_rect.y + 16))
        conn_text = SMALL_FONT.render(
            f"Connections: {self.connection_count}/{self.connection_limit}",
            True,
            COLORS["text_dim"],
        )
        surface.blit(conn_text, (self._chat_rect.x + 12, self._chat_rect.y + 30))
        sid = SMALL_FONT.render(f"Session: {self.session_id[:16]}…", True, COLORS["text_dim"])
        surface.blit(sid, (self._chat_rect.x + 12, self._chat_rect.y + 44))
        channel = SMALL_FONT.render(f"Channel: {self.chat_channel}", True, COLORS["text_dim"])
        surface.blit(channel, (self._chat_rect.x + 12, self._chat_rect.y + 58))

        pygame.draw.rect(surface, COLORS["input_bg"], self._history_rect, border_radius=8)
        pygame.draw.rect(surface, COLORS["border"], self._history_rect, 1, border_radius=8)
        clip = surface.get_clip()
        surface.set_clip(self._history_rect)
        y = self._history_rect.y + 8 - self._chat_scroll
        for line in self.chat_lines:
            who = SMALL_FONT.render(f"{line.sender}:", True, COLORS["accent"])
            txt = SMALL_FONT.render(line.text[:120], True, COLORS["text"])
            surface.blit(who, (self._history_rect.x + 8, y))
            surface.blit(txt, (self._history_rect.x + 8, y + 18))
            y += 40
        surface.set_clip(clip)

        self._input.draw(surface)
        mp = pygame.mouse.get_pos()
        self._btn_send.draw(surface, self._btn_send.contains(mp))
        self._btn_leave.draw(surface, self._btn_leave.contains(mp))


# --- Screen enum helper for arcade_client ----------------------------------


class AppScreen(Enum):
    LOGIN = auto()
    BROWSER = auto()
    STATS = auto()
    GAME_STATS = auto()
    LEADERBOARD = auto()
    QUEUE = auto()
    PLAY = auto()


__all__ = (
    "COLORS",
    "TITLE_FONT",
    "BODY_FONT",
    "SMALL_FONT",
    "Button",
    "TextInput",
    "LoginScreen",
    "BrowserScreen",
    "GameInfo",
    "PlayerStats",
    "StatsScreen",
    "GameStatsScreen",
    "LeaderboardScreen",
    "QueueScreen",
    "PlaySessionScreen",
    "ChatLine",
    "AppScreen",
)