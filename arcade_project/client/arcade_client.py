"""
arcade_client.py - Central client class + game loop

Author: Team MOSFET
Date: Spring 2026
Lab: Final Project
"""

from __future__ import annotations

import os
import sys
import time
import threading
import pygame
from datastructures.array import ArrayList
from datastructures.hash_table import HashTable

from client.screens import (
    AppScreen,
    BrowserScreen,
    GameOverScreen,
    GameInfo,
    GameStatsScreen,
    LeaderboardScreen,
    LoginScreen,
    MatchHistoryScreen,
    PlayerSearchScreen,
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

def _build_game_list():
    games = ArrayList()
    games.append(GameInfo("deven",    "Where the Fog Remembers", "Horror/adventure · explore & chat",           "Deven Garland"))
    games.append(GameInfo("ellie",    "Eli's Legacy",            "Fantasy/adventure · compete for high score",  "Ellie Lutz"))
    games.append(GameInfo("kimberly", "Fate of the Fists",       "Adventure/combat · fight to win",             "Kimberly"))
    games.append(GameInfo("mennah",   "Doom in Delta",           "Historical RPG · complete secret missions",   "Mennah Dewidar"))
    games.append(GameInfo("vraj",     "Echoes of the Iron Realm","Top-down action RPG · real-time multiplayer", "Vraj"))
    return games


def _build_game_names(games):
    names = HashTable()
    for game in games:
        names[game.id] = game.name
    return names


GAME_LIST = _build_game_list()
GAME_NAMES = _build_game_names(GAME_LIST)


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
        self._chat_shown = HashTable()
        self._chat_channel = "global"
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
            on_history=self._handle_history,
            on_leaderboard=self._handle_leaderboard,
            on_player_search=self._handle_player_search,
            on_star=self._handle_star,
            on_rate=self._handle_rate,
            on_search_players=self._handle_search_players,
            on_select_player=self._handle_select_player,
            on_game_stats=self._handle_game_stats,
            games=GAME_LIST,
        )
        self._stats = StatsScreen(full, on_back=self._handle_back_to_browser)
        self._game_over = GameOverScreen(full, on_back=self._handle_back_to_browser)
        self._history = MatchHistoryScreen(
            full,
            on_back=self._handle_back_to_browser,
            on_refresh=self._load_history_data,
            games=GAME_LIST,
        )
        self._game_stats = GameStatsScreen(full, on_back=self._handle_back_to_browser)
        self._player_search = PlayerSearchScreen(
            full,
            on_back=self._handle_back_to_browser,
            on_search_players=self._handle_search_players,
            on_select_player=self._handle_select_player,
            games=GAME_LIST,
        )
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
        if self._current == AppScreen.LOGIN:
            return self._login
        if self._current == AppScreen.BROWSER:
            return self._browser
        if self._current == AppScreen.STATS:
            return self._stats
        if self._current == AppScreen.HISTORY:
            return self._history
        if self._current == AppScreen.GAME_OVER:
            return self._game_over
        if self._current == AppScreen.GAME_STATS:
            return self._game_stats
        if self._current == AppScreen.PLAYER_SEARCH:
            return self._player_search
        if self._current == AppScreen.LEADERBOARD:
            return self._leaderboard
        if self._current == AppScreen.QUEUE:
            return self._queue
        return self._play

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
            ratings = HashTable()
            if resp.get("status") == "ok":
                for row in resp.get("data") or []:
                    game = row.get("game")
                    avg = row.get("avg_rating", 0)
                    if game:
                        ratings[game] = float(avg)
            self._browser.set_ratings(ratings)
        except Exception:
            self._browser.set_ratings(HashTable())

    def _handle_play(self, game_id: str) -> None:
        self._current_game_id = game_id
        game_name = next((g.name for g in GAME_LIST if g.id == game_id), game_id)
        self._queue.game_name = game_name
        self._queue.set_detail("Talking to matchmaker...")
        self._go_to(AppScreen.QUEUE)
        try:
            resp = self._conn.join_queue(self._current_game_id or "global")
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
                games_played=int(self._conn._request("get_player_stats", {"username": self._username}).get("data", {}).get("games_played", 0)),
                messages_sent=int(messages) if messages else 0,
                favorite_game=fav_name,
                minutes_played=int(minutes) if minutes else 0,
            ))
        except Exception:
            pass
        self._go_to(AppScreen.STATS)

    def _handle_player_search(self) -> None:
        self._go_to(AppScreen.PLAYER_SEARCH)

    def _handle_game_stats(self, game_id: str) -> None:
        game_name = GAME_NAMES.get(game_id, game_id) if game_id else game_id
        stat_keys = ("score", "sessions", "play_time", "chats", "deaths", "disconnects")
        stats = HashTable()
        for stat in stat_keys:
            stats[stat] = HashTable()
            stats[stat]["rank"] = None
            stats[stat]["value"] = 0
            try:
                top_resp = self._conn.get_game_leaderboard(game_id, stat=stat, top_n=250)
                if top_resp.get("status") == "ok":
                    top_rows = top_resp.get("data") or ()
                    for idx, entry in enumerate(top_rows):
                        entry_str = str(entry)
                        parts = entry_str.split(":")
                        if len(parts) != 2:
                            continue
                        name = parts[0].strip()
                        if name != self._username:
                            continue
                        raw_value = parts[1].strip()
                        try:
                            stats[stat]["value"] = int(float(raw_value))
                        except Exception:
                            stats[stat]["value"] = raw_value
                        stats[stat]["rank"] = idx + 1
                        break
                if stats[stat]["rank"] is None:
                    rank_resp = self._conn.get_player_rank(self._username, game_id, stat=stat)
                    if rank_resp.get("status") == "ok":
                        stats[stat]["rank"] = rank_resp.get("data")
            except Exception:
                pass

        self._game_stats.set_stats(game_name, stats)
        self._go_to(AppScreen.GAME_STATS)

    def _load_history_data(self, game: str, outcome: str, start_date, end_date):
        rows = ArrayList()
        game_filter = None if game in (None, "", "all") else game
        history = self._conn.get_player_history_sorted(
            self._username,
            sort_by="date",
            descending=True,
            game=game_filter,
            start_date=start_date,
            end_date=end_date,
            outcome=outcome or "all",
        )
        for row in history:
            rows.append(row)
        return rows

    def _handle_history(self) -> None:
        self._history.refresh()
        self._go_to(AppScreen.HISTORY)

    def _handle_back_to_browser(self) -> None:
        if self._leaderboard_from_play and self._session_id:
            self._leaderboard_from_play = False
            self._go_to(AppScreen.PLAY)
            return
        self._go_to(AppScreen.BROWSER)

    def _load_leaderboard_data(self, game_id: str, stat: str, top_n: int = 10):
        top_rows = ArrayList()
        range_rows = ArrayList()
        rank_value = None

        top_resp = self._conn.get_game_leaderboard(game_id, stat=stat, top_n=10)
        if top_resp.get("status") == "ok":
            for row in (top_resp.get("data") or ()):
                top_rows.append(str(row))
        elif "bad request parameters" in str(top_resp.get("message", "")):
            legacy_top = self._conn.get_leaderboard(top_n=10)
            if legacy_top.get("status") == "ok":
                for row in (legacy_top.get("data") or ()):
                    top_rows.append(str(row))

        rank_resp = self._conn.get_player_rank(self._username, game_id, stat=stat)
        if rank_resp.get("status") == "ok":
            rank_value = rank_resp.get("data")

        range_resp = self._conn.get_game_leaderboard(game_id, stat=stat, top_n=int(top_n))
        if range_resp.get("status") == "ok":
            for row in (range_resp.get("data") or ()):
                range_rows.append(str(row))
        elif "bad request parameters" in str(range_resp.get("message", "")):
            legacy_range = self._conn.get_leaderboard(top_n=int(top_n))
            if legacy_range.get("status") == "ok":
                for row in (legacy_range.get("data") or ()):
                    range_rows.append(str(row))

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
            return ArrayList()

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
            resp = self._conn.send_chat(
                text,
                chat_channel=self._chat_channel if self._session_id else None,
                game=self._current_game_id or "global",
            )
            if resp.get("status") == "ok" and resp.get("data") is True:
                self._play.add_chat(self._username, text)
            else:
                self._play.add_chat("server", "Message blocked or not delivered.")
        except Exception as e:
            print(f"[chat] send error: {e}")
            self._play.add_chat("server", "Message failed to send.")

    def _handle_leave(self, reason: str = "disconnect") -> None:
        elapsed_seconds = 0
        if self._session_start_time is not None:
            elapsed_seconds = max(0, int(time.time() - self._session_start_time))
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
            final_score = 0
            if self._ellie_game is not None:
                try:
                    final_score = int(getattr(self._ellie_game, "score", 0))
                except Exception:
                    final_score = 0
            game_name = self._current_game_id or "global"
            elapsed_minutes = 0
            if elapsed_seconds > 0:
                elapsed_minutes = max(1, int((elapsed_seconds + 59) // 60))
            end_game_payload = HashTable()
            end_game_payload["game_id"] = int(self._session_id)
            end_game_payload["players"] = [self._username]
            end_game_payload["winner"] = self._username
            end_game_payload["score"] = final_score
            end_game_payload["game"] = game_name
            end_game_payload["duration"] = elapsed_seconds
            end_resp = None
            try:
                end_resp = self._conn._request("end_game", end_game_payload)
                if end_resp.get("status") == "error":
                    msg = str(end_resp.get("message", ""))
                    if "unexpected keyword argument 'duration'" in msg:
                        fallback_payload = HashTable()
                        for key in end_game_payload:
                            if key != "duration":
                                fallback_payload[key] = end_game_payload[key]
                        end_resp = self._conn._request("end_game", fallback_payload)
                if end_resp.get("status") == "error":
                    msg = str(end_resp.get("message", ""))
                    if "unexpected keyword argument 'game'" in msg:
                        minimal_payload = HashTable()
                        minimal_payload["game_id"] = end_game_payload["game_id"]
                        minimal_payload["players"] = end_game_payload["players"]
                        minimal_payload["winner"] = end_game_payload["winner"]
                        minimal_payload["score"] = end_game_payload["score"]
                        end_resp = self._conn._request("end_game", minimal_payload)
                if end_resp.get("status") == "error":
                    self._conn._request(
                        "record_session_result",
                        self._conn._payload((
                            ("game", game_name),
                            ("username", self._username),
                            ("score", final_score),
                            ("play_time", elapsed_minutes),
                        )),
                    )
                if end_resp.get("status") == "error":
                    print(f"[leave] end_game error: {end_resp.get('message')}")
            except Exception as e:
                print(f"[leave] end_game error: {e}")

        self._conn.clear_session()

        if self._ellie_game is not None:
            try:
                self._ellie_game.cleanup()
            except Exception as e:
                print(f"[leave] cleanup error: {e}")

        self._play.clear_chat()
        self._chat_shown = HashTable()
        self._session_id = ""
        self._chat_channel = "global"
        self._ellie_game = None
        if reason == "death":
            game_name = GAME_NAMES.get(self._current_game_id, self._current_game_id) if self._current_game_id else "Game"
            self._game_over.set_context(game_name, "Health reached 0.")
            self._go_to(AppScreen.GAME_OVER)
        else:
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
        self._chat_channel = f"{self._current_game_id}:{session_id}" if self._current_game_id else str(session_id)
        self._play.set_chat_channel(self._chat_channel)
        self._play.add_chat("server", "Match found! Game starting...")
        self._chat_shown = HashTable()

        if self._current_game_id == "ellie":
            try:
                from arcade_project.games.ellie_game.game import EllieGame
                game_surface = self._play.game_subsurface(self._screen)
                self._ellie_game = EllieGame(game_surface, self._username)
            except Exception as e:
                print(f"[ellie_game] Failed to load: {e}")
                self._ellie_game = None
        elif self._current_game_id in ("deven", "kimberly", "mennah", "vraj"):
            try:
                game_surface = self._play.game_subsurface(self._screen)
                if self._current_game_id == "deven":
                    from arcade_project.games.deven_game.game import DevenGame
                    self._ellie_game = DevenGame(game_surface, self._username)
                elif self._current_game_id == "kimberly":
                    from arcade_project.games.kimberly_game.game import KimberlyGame
                    self._ellie_game = KimberlyGame(game_surface, self._username)
                elif self._current_game_id == "mennah":
                    from arcade_project.games.mennah_game.game import MennahGame
                    self._ellie_game = MennahGame(game_surface, self._username)
                elif self._current_game_id == "vraj":
                    from arcade_project.games.vraj_game.game import VrajGame
                    self._ellie_game = VrajGame(game_surface, self._username)
            except Exception as e:
                print(f"[{self._current_game_id}_game] Failed to load: {e}")
                self._ellie_game = None
        else:
            self._ellie_game = None

        if self._ellie_game is not None and hasattr(self._ellie_game, "level") and self._ellie_game.level:
            try:
                self._ellie_game.level.network.game_id = self._chat_channel
            except Exception:
                pass

        self._go_to(AppScreen.PLAY)

    def _sync_play_connections_from_game(self) -> None:
        if not self._play or not self._ellie_game:
            return
        level = getattr(self._ellie_game, "level", None)
        if not level:
            return
        try:
            others = getattr(level, "other_players", None)
            if others is None:
                return
            current_players = max(1, int(len(others)) + 1)
            self._play.set_connection_status(current_players, 30)
        except Exception:
            pass

    def _poll_server(self) -> None:
        if self._current == AppScreen.QUEUE:
            try:
                resp = self._conn._request(
                    "try_create_match",
                    self._conn._payload((
                        ("username", self._username),
                        ("game", self._current_game_id or "global"),
                    )),
                )
                if resp.get("status") != "ok":
                    message = str(resp.get("message", ""))
                    if "bad request parameters" in message:
                        resp = self._conn._request("try_create_match")
                if resp.get("status") == "ok":
                    data = resp.get("data") or HashTable()
                    session_id = data.get("game_id") if hasattr(data, "get") else None
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
                chat_data = self._conn.poll_chat(self._chat_channel or self._session_id)
                messages = chat_data.get("messages", ArrayList()) if hasattr(chat_data, "get") else ArrayList()
                for msg in messages:
                    key = f"{msg.get('sender')}|{msg.get('message')}|{msg.get('time')}"
                    if key not in self._chat_shown and msg.get("sender") != self._username:
                        self._play.add_chat(msg["sender"], msg["message"], msg.get("time", 0.0))
                        self._chat_shown[key] = True
            except Exception as e:
                print(f"[poll chat] {e}")

            try:
                status = self._conn.get_instance_status(self._session_id)
                current_players = status.get("current_players", 0)
                max_players = status.get("max_players", 30)
                self._play.set_connection_status(current_players, max_players)
            except Exception:
                pass
            self._sync_play_connections_from_game()

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
                elif (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_TAB
                    and self._current in (AppScreen.PLAY, AppScreen.LEADERBOARD)
                ):
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
                    self._sync_play_connections_from_game()
                    if self._ellie_game.state == "done":
                        reason = getattr(self._ellie_game, "leave_reason", None) or "disconnect"
                        self._handle_leave(reason=reason)
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