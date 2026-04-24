"""
arcade_client.py - Central client class + game loop

Manages screen transitions and wires all callbacks from screens.py
to the connection layer. Run via client.py at the project root.

Author: Team MOSFET
Date: Spring 2026
Lab: Final Project
"""

import os
import sys
import threading
import pygame

from client.screens import (
    AppScreen,
    BrowserScreen,
    GameInfo,
    LoginScreen,
    PlayerStats,
    PlaySessionScreen,
    QueueScreen,
    StatsScreen,
    COLORS,
    SMALL_FONT,
)
from client.connection import ServerConnection


# Window settings
WINDOW_W = 1024
WINDOW_H = 680
FPS = 60
WINDOW_TITLE = "MOSFET Arcade"

# Server settings (overridable for laptops connecting to ece)
SERVER_HOST = os.environ.get("ARCADE_PLATFORM_HOST", "127.0.0.1")
SERVER_PORT = int(os.environ.get("ARCADE_PLATFORM_PORT", "9000"))

# Hardcoded game list (no server endpoint for this yet)
GAME_LIST = [
    GameInfo("deven",    "Deven's Game",    "Fast reflex mini-game"),
    GameInfo("ellie",    "Ellie's Game",    "Puzzle challenge"),
    GameInfo("kimberly", "Kimberly's Game", "Score attack"),
    GameInfo("mennah",   "Mennah's Game",   "Strategy lite"),
    GameInfo("vraj",     "Vraj's Game",     "Endless runner"),
]


class ArcadeClient:
    """
    Top-level client. Owns the pygame window, the server connection,
    and all screen objects. Drives the main loop.
    """

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption(WINDOW_TITLE)
        self._clock = pygame.time.Clock()
        self._running = False

        # Current screen state
        self._current = AppScreen.LOGIN
        self._username = ""
        self._current_game_id = ""
        self._session_id = ""
        self._chat_shown = set()
        self._ellie_game = None

        # Connect to platform server (env wins over module defaults)
        _host = os.environ.get("ARCADE_PLATFORM_HOST", SERVER_HOST)
        _port = int(os.environ.get("ARCADE_PLATFORM_PORT", str(SERVER_PORT)))
        self._conn = ServerConnection(_host, _port)
        try:
            self._conn.connect()
            self._connected = True
        except Exception as e:
            print(f"[warn] Could not connect to server: {e}")
            self._connected = False

        # Build all screens
        full = self._screen.get_rect()
        self._login = LoginScreen(
            full,
            on_login=self._handle_login,
            on_register=self._handle_register,
        )
        self._browser = BrowserScreen(
            full,
            on_play=self._handle_play,
            on_logout=self._handle_logout,
            on_stats=self._handle_stats,
            games=GAME_LIST,
        )
        self._stats = StatsScreen(
            full,
            on_back=self._handle_back_to_browser,
        )
        self._queue = QueueScreen(
            full,
            game_name="",
            on_cancel=self._handle_cancel_queue,
        )
        self._play = PlaySessionScreen(
            full,
            game_title="",
            session_id="",
            on_send_chat=self._handle_send_chat,
            on_leave=self._handle_leave,
        )

        if not self._connected:
            self._login.set_status("Could not reach server. Check your connection.", error=True)

    # --- Screen helpers ----------------------------------------------------

    def _go_to(self, screen: AppScreen) -> None:
        self._current = screen

    def _active_screen(self):
        return {
            AppScreen.LOGIN:   self._login,
            AppScreen.BROWSER: self._browser,
            AppScreen.STATS:   self._stats,
            AppScreen.QUEUE:   self._queue,
            AppScreen.PLAY:    self._play,
        }[self._current]

    # --- Login callbacks ---------------------------------------------------

    def _handle_login(self, username: str, password: str) -> None:
        if not username or not password:
            self._login.set_status("Enter a username and password.", error=True)
            return
        try:
            resp = self._conn.login(username, password)
            if resp.get("status") == "ok" and resp.get("data") is True:
                self._username = username
                self._login.set_status(f"Welcome back, {username}!", error=False)
                self._go_to(AppScreen.BROWSER)
            else:
                self._login.set_status("Invalid username or password.", error=True)
        except Exception as e:
            self._login.set_status(f"Server error: {e}", error=True)

    def _handle_register(self, username: str, password: str) -> None:
        if not username or not password:
            self._login.set_status("Enter a username and password.", error=True)
            return
        try:
            email = f"{username}@arcade.local"
            resp = self._conn.register(username, password, email)
            if resp.get("status") == "ok" and resp.get("data") is True:
                self._username = username
                self._conn.login(username, password)
                self._login.set_status(f"Account created! Welcome, {username}!", error=False)
                self._go_to(AppScreen.BROWSER)
            else:
                self._login.set_status("Username already taken.", error=True)
        except Exception as e:
            self._login.set_status(f"Server error: {e}", error=True)

    # --- Browser callbacks -------------------------------------------------

    def _handle_play(self, game_id: str) -> None:
        self._current_game_id = game_id
        game_name = next((g.name for g in GAME_LIST if g.id == game_id), game_id)
        self._queue.game_name = game_name
        self._queue.set_detail("Talking to matchmaker...")
        self._go_to(AppScreen.QUEUE)
        try:
            resp = self._conn.join_queue()
            if resp.get("status") == "ok":
                self._queue.set_detail("In queue — waiting for opponent...")
            else:
                self._queue.set_detail(f"Error: {resp.get('message', 'Queue failed')}")
        except Exception as e:
            self._queue.set_detail(f"Server error: {e}")

    def _handle_logout(self) -> None:
        self._conn.disconnect()
        try:
            self._conn.connect()
        except Exception:
            pass
        self._username = ""
        self._ellie_game = None
        self._login.set_status("Logged out.", error=False)
        self._go_to(AppScreen.LOGIN)

    def _handle_stats(self) -> None:
        try:
            resp = self._conn.get_leaderboard(10)
            if resp.get("status") == "ok":
                data = resp.get("data", {})
                entries = data.get("leaderboard", []) if isinstance(data, dict) else []
                my_entry = next((e for e in entries if e.get("username") == self._username), {})
                self._stats.set_stats(PlayerStats(
                    games_played=my_entry.get("games_played", 0),
                    messages_sent=0,
                    friends=0,
                    hours_playing=my_entry.get("hours_playing", 0.0),
                ))
        except Exception:
            pass
        self._go_to(AppScreen.STATS)

    def _handle_back_to_browser(self) -> None:
        self._go_to(AppScreen.BROWSER)

    # --- Queue callbacks ---------------------------------------------------

    def _handle_cancel_queue(self) -> None:
        self._ellie_game = None
        self._go_to(AppScreen.BROWSER)

    # --- Play session callbacks --------------------------------------------

    def _handle_send_chat(self, text: str) -> None:
        try:
            self._conn.send_chat(text)
        except Exception as e:
            print(f"[chat] send error: {e}")
        self._play.add_chat(self._username, text)

    def _handle_leave(self) -> None:
        self._play.clear_chat()
        self._chat_shown.clear()
        self._session_id = ""
        self._ellie_game = None
        self._go_to(AppScreen.BROWSER)

    # --- Match found -------------------------------------------------------

    def _on_match_found(self, session_id: str) -> None:
        self._session_id = session_id
        game_name = next(
            (g.name for g in GAME_LIST if g.id == self._current_game_id),
            self._current_game_id,
        )
        full = self._screen.get_rect()
        self._play = PlaySessionScreen(
            full,
            game_title=game_name,
            session_id=session_id,
            on_send_chat=self._handle_send_chat,
            on_leave=self._handle_leave,
        )
        self._play.add_chat("server", "Match found! Game starting...")
        self._chat_shown.clear()

        # Launch Ellie's game inline in the left panel
        if self._current_game_id == "ellie":
            try:
                from arcade_project.games.ellie_game.game import EllieGame
                game_surface = self._play.game_subsurface(self._screen)
                self._ellie_game = EllieGame(game_surface, self._username)
            except Exception as e:
                print(f"[ellie_game] Failed to load: {e}")
                self._ellie_game = None
        else:
            self._ellie_game = None

        self._go_to(AppScreen.PLAY)

    # --- Server polling ----------------------------------------------------

    def _poll_server(self) -> None:
        if self._current == AppScreen.QUEUE:
            try:
                resp = self._conn._request("try_create_match", {})
                if resp.get("status") == "ok":
                    data = resp.get("data") or {}
                    session_id = data.get("game_id") if isinstance(data, dict) else None
                    if session_id:
                        self._on_match_found(str(session_id))
            except Exception as e:
                print(f"[poll queue] {e}")

        elif self._current == AppScreen.PLAY and self._session_id:
            try:
                resp = self._conn._request("get_chat", {"game_id": self._session_id})
                if resp.get("status") == "ok":
                    data = resp.get("data") or {}
                    messages = data.get("messages", []) if isinstance(data, dict) else []
                    for msg in messages:
                        key = (msg.get("sender"), msg.get("message"), msg.get("time"))
                        if key not in self._chat_shown and msg.get("sender") != self._username:
                            self._play.add_chat(
                                msg["sender"],
                                msg["message"],
                                msg.get("time", 0.0),
                            )
                            self._chat_shown.add(key)
            except Exception as e:
                print(f"[poll chat] {e}")

    # --- Main loop ---------------------------------------------------------

    def run(self) -> None:
        self._running = True
        poll_timer = 0.0
        POLL_INTERVAL = 0.5

        while self._running:
            dt = self._clock.tick(FPS) / 1000.0
            active = self._active_screen()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                else:
                    active.handle_event(event)
                    if self._ellie_game and self._current == AppScreen.PLAY:
                        self._ellie_game.handle_event(event)

            active.update(dt)

            if self._ellie_game and self._current == AppScreen.PLAY:
                try:
                    self._ellie_game.update(dt)
                except Exception as e:
                    print(f"[ellie_game] update error: {e}")

            poll_timer += dt
            if poll_timer >= POLL_INTERVAL and self._connected:
                poll_timer = 0.0
                try:
                    self._poll_server()
                except Exception as e:
                    print(f"[poll] {e}")

            self._screen.fill(COLORS["bg"])
            active.draw(self._screen)

            if self._ellie_game and self._current == AppScreen.PLAY:
                try:
                    self._ellie_game.draw()
                except Exception as e:
                    print(f"[ellie_game] draw error: {e}")

            if self._username:
                info = SMALL_FONT.render(
                    f"{self._username}  |  {self._current.name}",
                    True,
                    COLORS["text_dim"],
                )
                self._screen.blit(info, (12, WINDOW_H - 24))

            pygame.display.flip()

        self._conn.disconnect()
        pygame.quit()
        sys.exit(0)