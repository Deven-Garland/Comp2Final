"""
UI screens for the arcade client (pygame).

Screens: Login, Game Browser, Match Queue, Play Session (game area + chat).

Wire callbacks from arcade_client / connection layer; this module only handles
drawing and input.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List, Optional, Tuple

import pygame


# --- Theme -----------------------------------------------------------------

COLORS = {
    "bg": (18, 18, 28),
    "panel": (28, 28, 42),
    "panel_light": (38, 38, 58),
    "accent": (94, 234, 212),
    "accent_dim": (60, 160, 145),
    "text": (240, 240, 245),
    "text_dim": (160, 160, 180),
    "error": (255, 120, 120),
    "success": (120, 220, 160),
    "border": (70, 70, 95),
    "input_bg": (22, 22, 35),
    "row_hover": (45, 45, 68),
    "row_sel": (55, 55, 85),
}


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
            self.focused = self.rect.collidepoint(event.pos)
            return self.focused
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
        games: Optional[List[GameInfo]] = None,
    ):
        self.rect = rect
        self.on_play = on_play
        self.on_logout = on_logout
        self.games: List[GameInfo] = games or [
            GameInfo("deven", "Deven's Game", "Fast reflex mini-game"),
            GameInfo("ellie", "Ellie's Game", "Puzzle challenge"),
            GameInfo("kimberly", "Kimberly's Game", "Score attack"),
            GameInfo("mennah", "Mennah's Game", "Strategy lite"),
            GameInfo("vraj", "Vraj's Game", "Endless runner"),
        ]
        self._selected: Optional[int] = None
        self._scroll = 0
        self._hover_row = -1
        pad = 24
        self._list_rect = pygame.Rect(rect.x + pad, rect.y + 100, rect.width - 2 * pad, rect.height - 200)
        self._btn_play = Button(pygame.Rect(rect.right - pad - 160, rect.bottom - 72, 150, 44), "Find match")
        self._btn_out = Button(pygame.Rect(rect.x + pad, rect.bottom - 72, 120, 44), "Log out")

    def set_games(self, games: List[GameInfo]) -> None:
        self.games = games
        self._selected = None
        self._scroll = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._btn_play.contains(event.pos) and self._selected is not None:
                gid = self.games[self._selected].id
                self.on_play(gid)
            elif self._btn_out.contains(event.pos):
                self.on_logout()
            elif self._list_rect.collidepoint(event.pos):
                row_h = 56
                y = event.pos[1] - self._list_rect.y + self._scroll
                idx = y // row_h
                if 0 <= idx < len(self.games):
                    self._selected = idx
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

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLORS["bg"], self.rect)
        t = TITLE_FONT.render("Games", True, COLORS["text"])
        surface.blit(t, (self.rect.x + 24, self.rect.y + 24))
        sub = SMALL_FONT.render("Select a title, then find a match.", True, COLORS["text_dim"])
        surface.blit(sub, (self.rect.x + 24, self.rect.y + 72))

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
        surface.set_clip(clip)

        mp = pygame.mouse.get_pos()
        self._btn_play.enabled = self._selected is not None
        self._btn_play.draw(surface, self._btn_play.contains(mp))
        self._btn_out.draw(surface, self._btn_out.contains(mp))


# --- Queue / waiting -------------------------------------------------------


class QueueScreen:
    def __init__(self, rect: pygame.Rect, game_name: str, on_cancel: Callable[[], None]):
        self.rect = rect
        self.game_name = game_name
        self.on_cancel = on_cancel
        self.detail = "Talking to matchmaker..."
        pad = 24
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
        # simple spinner arc
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
    """
    Left: game viewport placeholder (your game draws here or subprocess).
    Right: chat panel with history + input.
    """

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
        self.on_send_chat = on_send_chat
        self.on_leave = on_leave
        self.chat_lines: List[ChatLine] = []
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
        self._btn_send = Button(
            pygame.Rect(self._chat_rect.right - pad - 80, self._chat_rect.bottom - 52, 76, 36),
            "Send",
        )
        self._btn_leave = Button(pygame.Rect(rect.x + 16, rect.y + 16, 100, 36), "Leave")

    def add_chat(self, sender: str, text: str, timestamp: float = 0.0) -> None:
        self.chat_lines.append(ChatLine(sender=sender, text=text, timestamp=timestamp))
        total_h = len(self.chat_lines) * 40 + 8
        self._chat_scroll = max(0, total_h - self._history_rect.height)

    def clear_chat(self) -> None:
        self.chat_lines.clear()
        self._chat_scroll = 0

    def game_subsurface(self, surface: pygame.Surface) -> pygame.Surface:
        return surface.subsurface(self._game_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        self._input.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._btn_send.contains(event.pos):
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
        sid = SMALL_FONT.render(f"Session: {self.session_id[:16]}…", True, COLORS["text_dim"])
        surface.blit(sid, (self._chat_rect.x + 12, self._chat_rect.y + 44))

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
    QUEUE = auto()
    PLAY = auto()


__all__ = [
    "COLORS",
    "TITLE_FONT",
    "BODY_FONT",
    "SMALL_FONT",
    "Button",
    "TextInput",
    "LoginScreen",
    "BrowserScreen",
    "GameInfo",
    "QueueScreen",
    "PlaySessionScreen",
    "ChatLine",
    "AppScreen",
]


def _run_ui_demo() -> None:
    """Open a window to preview screens. Keys 1–4 switch views; Esc quits."""
    pygame.init()
    w, h = 960, 640
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("Arcade UI preview — 1 Login 2 Browser 3 Queue 4 Play — Esc quit")
    clock = pygame.time.Clock()
    full = screen.get_rect()

    login = LoginScreen(
        full,
        on_login=lambda u, p: login.set_status(f"Would log in: {u!r}", False),
        on_register=lambda u, p: login.set_status(f"Would register: {u!r}", False),
    )

    state: dict = {"queue_name": "Pick a game on screen 2"}

    def on_play(gid: str) -> None:
        name = next((g.name for g in browser.games if g.id == gid), gid)
        state["queue_name"] = name

    browser = BrowserScreen(full, on_play=on_play, on_logout=lambda: login.set_status("Logout (demo)", False))

    queue = QueueScreen(full, state["queue_name"], on_cancel=lambda: queue.set_detail("Cancelled (demo)"))
    play = PlaySessionScreen(
        full,
        game_title="Demo Game",
        session_id="demo-session-001",
        on_send_chat=lambda t: play.add_chat("You", t),
        on_leave=lambda: None,
    )
    play.add_chat("server", "Welcome to the session.")
    play.add_chat("teammate", "glhf")

    screens_order = (
        ("Login", login),
        ("Browser", browser),
        ("Queue", queue),
        ("Play", play),
    )
    idx = 0
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    idx = 0
                elif event.key == pygame.K_2:
                    idx = 1
                elif event.key == pygame.K_3:
                    idx = 2
                    queue.game_name = state["queue_name"]
                elif event.key == pygame.K_4:
                    idx = 3
            else:
                screens_order[idx][1].handle_event(event)

        active = screens_order[idx][1]
        active.update(dt)
        screen.fill(COLORS["bg"])
        active.draw(screen)
        hint = SMALL_FONT.render(
            f"Screen: {screens_order[idx][0]}  |  1–4 switch  |  Esc quit",
            True,
            COLORS["text_dim"],
        )
        screen.blit(hint, (12, h - 28))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    _run_ui_demo()
