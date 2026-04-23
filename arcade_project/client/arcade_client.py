"""
arcade_client.py - Central client class + game loop

Manages screen transitions and wires all callbacks from screens.py
to the connection layer. Run via client.py at the project root.

Author: Team MOSFET
Date: Spring 2026
Lab: Final Project
"""

import sys
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

        # Server connection (wraps TCP sockets to platform + game server)
        self._conn = ServerConnection()

        # Build all screens up front — they're cheap to keep alive
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

    # --- Screen helpers ----------------------------------------------------

    def _go_to(self, screen: AppScreen) -> None:
        self._current = screen

    def _active_screen(self):
        """Return whichever screen object is currently active."""
        return {
            AppScreen.LOGIN: self._login,
            AppScreen.BROWSER: self._browser,
            AppScreen.STATS: self._stats,
            AppScreen.QUEUE: self._queue,
            AppScreen.PLAY: self._play,
        }[self._current]

    # --- Login callbacks ---------------------------------------------------

    def _handle_login(self, username: str, password: str) -> None:
        if not username or not password:
            self._login.set_status("Enter a username and password.", error=True)
            return
        ok, msg = self._conn.login(username, password)
        if ok:
            self._username = username
            self._login.set_status(f"Welcome back, {username}!", error=False)
            self._refresh_browser()
            self._go_to(AppScreen.BROWSER)
        else:
            self._login.set_status(msg or "Login failed.", error=True)

    def _handle_register(self, username: str, password: str) -> None:
        if not username or not password:
            self._login.set_status("Enter a username and password.", error=True)
            return
        ok, msg = self._conn.register(username, password)
        if ok:
            self._username = username
            self._login.set_status(f"Account created! Welcome, {username}!", error=False)
            self._refresh_browser()
            self._go_to(AppScreen.BROWSER)
        else:
            self._login.set_status(msg or "Registration failed.", error=True)

    # --- Browser callbacks -------------------------------------------------

    def _refresh_browser(self) -> None:
        """Pull game list from server and update browser."""
        games = self._conn.get_game_list()
        if games:
            self._browser.set_games([GameInfo(g["id"], g["name"], g.get("description", "")) for g in games])

    def _handle_play(self, game_id: str) -> None:
        self._current_game_id = game_id
        game_name = next((g.name for g in self._browser.games if g.id == game_id), game_id)
        self._queue.game_name = game_name
        self._queue.set_detail("Talking to matchmaker...")
        self._go_to(AppScreen.QUEUE)
        # Ask the server to queue us up
        ok, msg = self._conn.join_queue(game_id)
        if ok:
            self._queue.set_detail(msg or "In queue — waiting for opponent...")
        else:
            self._queue.set_detail(f"Error: {msg}")

    def _handle_logout(self) -> None:
        self._conn.logout()
        self._username = ""
        self._login.set_status("Logged out.", error=False)
        self._go_to(AppScreen.LOGIN)

    def _handle_stats(self) -> None:
        raw = self._conn.get_stats(self._username)
        if raw:
            self._stats.set_stats(PlayerStats(
                games_played=raw.get("games_played", 0),
                messages_sent=raw.get("messages_sent", 0),
                friends=raw.get("friends", 0),
                hours_playing=raw.get("hours_playing", 0.0),
            ))
        self._go_to(AppScreen.STATS)

    def _handle_back_to_browser(self) -> None:
        self._go_to(AppScreen.BROWSER)

    # --- Queue callbacks ---------------------------------------------------

    def _handle_cancel_queue(self) -> None:
        self._conn.leave_queue()
        self._go_to(AppScreen.BROWSER)

    # --- Play session callbacks --------------------------------------------

    def _handle_send_chat(self, text: str) -> None:
        self._conn.send_chat(self._session_id, self._username, text)
        # Optimistically show the message right away
        self._play.add_chat(self._username, text)

    def _handle_leave(self) -> None:
        self._conn.leave_session(self._session_id)
        self._play.clear_chat()
        self._go_to(AppScreen.BROWSER)

    # --- Match found (called when server notifies us) ----------------------

    def _on_match_found(self, session_id: str) -> None:
        """Transition from queue → play when the server finds a match."""
        self._session_id = session_id
        game_name = next(
            (g.name for g in self._browser.games if g.id == self._current_game_id),
            self._current_game_id,
        )
        # Rebuild play screen with fresh session info
        full = self._screen.get_rect()
        self._play = PlaySessionScreen(
            full,
            game_title=game_name,
            session_id=session_id,
            on_send_chat=self._handle_send_chat,
            on_leave=self._handle_leave,
        )
        self._play.add_chat("server", "Match found! Game starting...")
        self._go_to(AppScreen.PLAY)

    # --- Server polling (chat + match notifications) -----------------------

    def _poll_server(self) -> None:
        """Check for incoming messages or match notifications."""
        if self._current == AppScreen.QUEUE:
            match = self._conn.poll_match()
            if match:
                self._on_match_found(match["session_id"])

        elif self._current == AppScreen.PLAY:
            messages = self._conn.poll_chat(self._session_id)
            for msg in messages:
                # Skip messages we sent ourselves (already shown optimistically)
                if msg.get("sender") != self._username:
                    self._play.add_chat(msg["sender"], msg["text"], msg.get("timestamp", 0.0))

    # --- Main loop ---------------------------------------------------------

    def run(self) -> None:
        self._running = True
        poll_timer = 0.0
        POLL_INTERVAL = 0.5  # seconds between server polls

        while self._running:
            dt = self._clock.tick(FPS) / 1000.0
            active = self._active_screen()

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                else:
                    active.handle_event(event)

            # Update
            active.update(dt)

            # Poll server periodically
            poll_timer += dt
            if poll_timer >= POLL_INTERVAL:
                poll_timer = 0.0
                try:
                    self._poll_server()
                except Exception as e:
                    # Don't crash the whole client on a network hiccup
                    print(f"[poll] {e}")

            # Draw
            self._screen.fill(COLORS["bg"])
            active.draw(self._screen)

            # Debug overlay — username + screen name in corner
            if self._username:
                info = SMALL_FONT.render(
                    f"{self._username}  |  {self._current.name}",
                    True,
                    COLORS["text_dim"],
                )
                self._screen.blit(info, (12, WINDOW_H - 24))

            pygame.display.flip()

        self._conn.close()
        pygame.quit()
        sys.exit(0)