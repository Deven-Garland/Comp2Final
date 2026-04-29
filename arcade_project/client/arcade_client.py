"""
arcade_client.py - Central client class + game loop

Author: Team MOSFET
Date: Spring 2026
Lab: Final Project
"""

import os
import sys
import time
import threading
import pygame

from client.screens import (
    AppScreen,
    BrowserScreen,
    GameInfo,
    LeaderboardScreen,
    LoginScreen,
    PlayerStats,
    PlaySessionScreen,
    QueueScreen,
    StatsScreen,
    COLORS,
    SMALL_FONT,
)
from client.connection import ServerConnection


WINDOW_W = 1024
WINDOW_H = 680
FPS = 60
WINDOW_TITLE = "MOSFET Arcade"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000

GAME_LIST = [
    GameInfo("deven",    "Deven's Game",    "Fast reflex mini-game"),
    GameInfo("ellie",    "Ellie's Game",    "Puzzle challenge"),
    GameInfo("kimberly", "Kimberly's Game", "Score attack"),
    GameInfo("mennah",   "Mennah's Game",   "Strategy lite"),
    GameInfo("vraj",     "Vraj's Game",     "Endless runner"),
]

GAME_NAMES = {g.id: g.name for g in GAME_LIST}


class ArcadeClient:
    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption(WINDOW_TITLE)
        self._clock = pygame.time.Clock()
        self._running = False

        self._current = AppScreen.LOGIN
        self._username = ""
        self._current_game_id = ""
        self._session_id = ""
        self._chat_shown = set()
        self._ellie_game = None
        self._session_start_time = None
        self._leaderboard_from_play = False

        self._conn = ServerConnection(SERVER_HOST, SERVER_PORT)
        try:
            self._conn.connect()
            self._connected = True
        except Exception as e:
            print(f"[warn] Could not connect to server: {e}")
            self._connected = False

        full = self._screen.get_rect()
        self._login = LoginScreen(full, on_login=self._handle_login, on_register=self._handle_register)
        self._browser = BrowserScreen(
            full,
            on_play=self._handle_play,
            on_logout=self._handle_logout,
            on_stats=self._handle_stats,
            on_leaderboard=self._handle_leaderboard,
            on_star=self._handle_star,
            on_rate=self._handle_rate,
            on_search_players=self._handle_search_players,
            on_select_player=self._handle_select_player,
            games=GAME_LIST,
        )
        self._stats = StatsScreen(full, on_back=self._handle_back_to_browser)
        self._leaderboard = LeaderboardScreen(
            full,
            on_back=self._handle_back_to_browser,
            on_refresh=self._load_leaderboard_data,
            games=GAME_LIST,
        )
        self._queue = QueueScreen(full, game_name="", on_cancel=self._handle_cancel_queue)
        self._play = PlaySessionScreen(
            full,
            game_title="",
            session_id="",
            on_send_chat=self._handle_send_chat,
            on_leave=self._handle_leave,
        )

        if not self._connected:
            self._login.set_status("Could not reach server. Check your connection.", error=True)

    def _go_to(self, screen: AppScreen) -> None:
        self._current = screen

    def _active_screen(self):
        return {
            AppScreen.LOGIN:   self._login,
            AppScreen.BROWSER: self._browser,
            AppScreen.STATS:   self._stats,
            AppScreen.LEADERBOARD: self._leaderboard,
            AppScreen.QUEUE:   self._queue,
            AppScreen.PLAY:    self._play,
        }[self._current]

    def _ensure_connected(self) -> bool:
        if self._connected:
            return True
        try:
            self._conn.disconnect()
            self._conn.connect()
            self._connected = True
            return True
        except Exception as e:
            self._login.set_status(f"Could not reach server: {e}", error=True)
            return False

    def _handle_login(self, username: str, password: str) -> None:
        if not username or not password:
            self._login.set_status("Enter a username and password.", error=True)
            return
        if not self._ensure_connected():
            return
        try:
            resp = self._conn.login(username, password)
            if resp.get("status") == "ok" and resp.get("data") is True:
                self._username = username
                self._login.set_status(f"Welcome back, {username}!", error=False)
                self._load_favorite()
                self._load_ratings()
                self._go_to(AppScreen.BROWSER)
            else:
                self._login.set_status("Invalid username or password.", error=True)
        except Exception as e:
            self._connected = False
            self._login.set_status(f"Server error: {e}", error=True)

    def _handle_register(self, username: str, password: str) -> None:
        if not username or not password:
            self._login.set_status("Enter a username and password.", error=True)
            return
        if not self._ensure_connected():
            return
        try:
            resp = self._conn.register(username, password)
            if resp.get("status") == "ok" and resp.get("data") is True:
                self._username = username
                self._conn.login(username, password)
                self._login.set_status(f"Account created! Welcome, {username}!", error=False)
                self._load_favorite()
                self._load_ratings()
                self._go_to(AppScreen.BROWSER)
            else:
                self._login.set_status("Username already taken.", error=True)
        except Exception as e:
            self._connected = False
            self._login.set_status(f"Server error: {e}", error=True)

    def _load_favorite(self) -> None:
        try:
            fav = self._conn.get_favorite(self._username)
            self._browser.set_favorite(fav or "")
        except Exception:
            pass

    def _load_ratings(self) -> None:
        try:
            resp = self._conn.get_rating_rankings()
            ratings = {}
            if resp.get("status") == "ok":
                for row in resp.get("data") or []:
                    game = row.get("game")
                    avg = row.get("avg_rating", 0)
                    if game:
                        ratings[game] = float(avg)
            self._browser.set_ratings(ratings)
        except Exception:
            self._browser.set_ratings({})

    def _handle_play(self, game_id: str) -> None:
        self._current_game_id = game_id
        game_name = next((g.name for g in GAME_LIST if g.id == game_id), game_id)
        self._queue.game_name = game_name
        self._queue.set_detail("Talking to matchmaker...")
        self._go_to(AppScreen.QUEUE)
        try:
            resp = self._conn.join_queue()
            if resp.get("status") == "ok" and resp.get("data") is True:
                self._queue.set_detail("In queue — waiting for opponent...")
            elif resp.get("status") == "ok":
                self._queue.set_detail("Queue rejected by server (are you logged in?).")
            else:
                self._queue.set_detail(f"Error: {resp.get('message', 'Queue failed')}")
        except Exception as e:
            self._queue.set_detail(f"Server error: {e}")

    def _handle_logout(self) -> None:
        if self._username:
            try:
                self._conn.report_disconnect(self._username, self._current_game_id or "global")
            except Exception:
                pass
        self._conn.disconnect()
        self._connected = False
        self._username = ""
        if self._ellie_game is not None:
            try:
                self._ellie_game.cleanup()
            except Exception:
                pass
        self._ellie_game = None
        self._login.set_status("Logged out.", error=False)
        self._go_to(AppScreen.LOGIN)

    def _handle_stats(self) -> None:
        try:
            minutes = self._conn.get_minutes(self._username)
            fav_id = self._conn.get_favorite(self._username)
            fav_name = GAME_NAMES.get(fav_id, fav_id) if fav_id else "None"
            messages = self._conn.get_messages_sent(self._username)
            self._stats.set_stats(PlayerStats(
                games_played=0,
                messages_sent=int(messages) if messages else 0,
                favorite_game=fav_name,
                minutes_played=int(minutes) if minutes else 0,
            ))
        except Exception:
            pass
        self._go_to(AppScreen.STATS)

    def _handle_back_to_browser(self) -> None:
        if self._leaderboard_from_play and self._session_id:
            self._leaderboard_from_play = False
            self._go_to(AppScreen.PLAY)
            return
        self._go_to(AppScreen.BROWSER)

    def _load_leaderboard_data(self, game_id: str, stat: str):
        top_rows = []
        range_rows = []
        rank_value = None

        top_resp = self._conn.get_game_leaderboard(game_id, stat=stat, top_n=10)
        if top_resp.get("status") == "ok":
            top_rows = [str(row) for row in (top_resp.get("data") or [])]

        rank_resp = self._conn.get_player_rank(self._username, game_id, stat=stat)
        if rank_resp.get("status") == "ok":
            rank_value = rank_resp.get("data")

        range_resp = self._conn.get_score_range(game_id, stat, 1, 1000000)
        if range_resp.get("status") == "ok":
            range_rows = [str(row) for row in (range_resp.get("data") or [])]

        return top_rows, rank_value, range_rows

    def _handle_leaderboard(self) -> None:
        self._leaderboard_from_play = False
        self._leaderboard.refresh()
        self._go_to(AppScreen.LEADERBOARD)

    def _toggle_leaderboard_hotkey(self) -> None:
        if self._current == AppScreen.PLAY:
            self._leaderboard_from_play = True
            self._leaderboard.refresh()
            self._go_to(AppScreen.LEADERBOARD)
        elif self._current == AppScreen.LEADERBOARD and self._leaderboard_from_play and self._session_id:
            self._leaderboard_from_play = False
            self._go_to(AppScreen.PLAY)

    def _handle_star(self, game_id: str) -> None:
        try:
            self._conn.set_favorite(self._username, game_id)
        except Exception as e:
            print(f"[star] {e}")

    def _handle_rate(self, game_id: str, stars: int) -> bool:
        try:
            resp = self._conn.rate_game(game_id, stars)
            ok = resp.get("status") == "ok"
            if ok:
                self._browser.set_user_rating(game_id, stars)
                self._load_ratings()
            return ok
        except Exception as e:
            print(f"[rate] {e}")
            return False

    def _handle_search_players(self, prefix: str):
        try:
            return self._conn.search_players(prefix)
        except Exception as e:
            print(f"[search] {e}")
            return []

    def _handle_select_player(self, username: str):
        try:
            return self._conn.get_player_profile(username)
        except Exception as e:
            print(f"[profile] {e}")
            return None

    def _handle_cancel_queue(self) -> None:
        self._ellie_game = None
        self._go_to(AppScreen.BROWSER)

    def _handle_send_chat(self, text: str) -> None:
        try:
            resp = self._conn.send_chat(text, game=self._current_game_id or "global")
            if resp.get("status") == "ok" and resp.get("data") is True:
                self._play.add_chat(self._username, text)
            else:
                self._play.add_chat("server", "Message blocked or not delivered.")
        except Exception as e:
            print(f"[chat] send error: {e}")
            self._play.add_chat("server", "Message failed to send.")

    def _handle_leave(self, reason: str = "disconnect") -> None:
        if self._session_start_time is not None:
            elapsed_minutes = int((time.time() - self._session_start_time) / 60)
            if elapsed_minutes > 0:
                try:
                    self._conn.add_minutes(self._username, elapsed_minutes)
                except Exception:
                    pass
            self._session_start_time = None

        if self._username:
            try:
                if reason == "death":
                    self._conn.report_death(self._username, self._current_game_id or "global")
                else:
                    self._conn.report_disconnect(self._username, self._current_game_id or "global")
            except Exception:
                pass

        if self._session_id:
            try:
                self._conn._request("end_game", {
                    "game_id": int(self._session_id),
                    "players": [self._username],
                    "winner": self._username,
                    "score": 0,
                    "game": self._current_game_id or "global",
                })
            except Exception as e:
                print(f"[leave] end_game error: {e}")

        self._conn.clear_session()

        if self._ellie_game is not None:
            try:
                self._ellie_game.cleanup()
            except Exception as e:
                print(f"[leave] cleanup error: {e}")

        self._play.clear_chat()
        self._chat_shown.clear()
        self._session_id = ""
        self._ellie_game = None
        self._go_to(AppScreen.BROWSER)

    def _on_match_found(self, session_id: str) -> None:
        self._session_id = session_id
        self._session_start_time = time.time()

        self._conn.set_session(session_id)

        game_name = next((g.name for g in GAME_LIST if g.id == self._current_game_id), self._current_game_id)
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

    def _poll_server(self) -> None:
        if self._current == AppScreen.QUEUE:
            try:
                resp = self._conn._request("try_create_match", {"username": self._username})
                # Backward compatibility: some server copies still use try_create_match() with no params.
                if resp.get("status") != "ok":
                    message = str(resp.get("message", ""))
                    if "bad request parameters" in message:
                        resp = self._conn._request("try_create_match")
                if resp.get("status") == "ok":
                    data = resp.get("data") or {}
                    session_id = data.get("game_id") if isinstance(data, dict) else None
                    if session_id:
                        try:
                            self._conn._request("acknowledge_match", {"username": self._username})
                        except Exception:
                            pass
                        self._on_match_found(str(session_id))
            except Exception as e:
                print(f"[poll queue] {e}")

        elif self._current == AppScreen.PLAY and self._session_id:
            try:
                try:
                    game_id = int(self._session_id)
                except (TypeError, ValueError):
                    game_id = self._session_id
                resp = self._conn._request("get_chat", {"game_id": game_id})
                if resp.get("status") == "ok":
                    data = resp.get("data") or {}
                    messages = data.get("messages", []) if isinstance(data, dict) else []
                    for msg in messages:
                        key = (msg.get("sender"), msg.get("message"), msg.get("time"))
                        if key not in self._chat_shown and msg.get("sender") != self._username:
                            self._play.add_chat(msg["sender"], msg["message"], msg.get("time", 0.0))
                            self._chat_shown.add(key)
            except Exception as e:
                print(f"[poll chat] {e}")

            try:
                status = self._conn.get_instance_status(self._session_id)
                current_players = status.get("current_players", 0)
                max_players = status.get("max_players", 30)
                self._play.set_connection_status(current_players, max_players)
            except Exception:
                pass

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
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                    self._toggle_leaderboard_hotkey()
                else:
                    active.handle_event(event)
                    if self._ellie_game and self._current == AppScreen.PLAY:
                        chat_focused_now = self._play.chat_input_focused
                        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION, pygame.MOUSEWHEEL):
                            self._ellie_game.handle_event(event)
                        elif not chat_focused_now:
                            self._ellie_game.handle_event(event)

            active.update(dt)

            if self._ellie_game and self._current == AppScreen.PLAY:
                self._ellie_game.chat_focused = self._play.chat_input_focused
                try:
                    self._ellie_game.update(dt)
                    if self._ellie_game.state == "done":
                        self._handle_leave(reason="death")
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