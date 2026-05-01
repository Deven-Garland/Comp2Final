# Platform server (you implement).
"""
server.py - Platform server runtime

Author: Mennah Khaled Dewidar
Date: [4/18/2026]
Lab: Final Project - Server
"""

import argparse
import json
import os
import socket
import socketserver
import sys
import threading
from pathlib import Path


if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))

from platform_server.accounts import Accounts
from platform_server.catalog import Catalog
from platform_server.chat import Chat
from platform_server.data_ingest import DataIngest
from platform_server.history import History
from platform_server.leaderboard import Leaderboard
from platform_server.matchmaking import Matchmaking
from .player_search import PlayerSearch
from platform_server.ratings import Ratings
from datastructures.array import ArrayList
from datastructures.hash_table import HashTable
from datastructures.sorting import insertion_sort


DEFAULT_HOST = os.getenv("PLATFORM_SERVER_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("PLATFORM_SERVER_PORT", "50070"))
DEFAULT_PLAYERS_PER_MATCH = int(os.getenv("PLATFORM_PLAYERS_PER_MATCH", "1"))
DEFAULT_MAX_PLAYERS_PER_INSTANCE = int(os.getenv("PLATFORM_MAX_PLAYERS_PER_INSTANCE", "30"))
DEFAULT_GAME_HOST = os.getenv("PLATFORM_GAME_HOST", "127.0.0.1")
GAME_SERVER_ENV = os.getenv("PLATFORM_GAME_SERVERS", "")
RUNTIME_STATE_FILE = Path(__file__).with_name("runtime_state.json")
RATINGS_STATE_FILE = Path(__file__).with_name("ratings_data.json")
LEADERBOARD_STATE_FILE = Path(__file__).with_name("leaderboard_data.json")

REQUEST_TYPE_KEYS = ("type", "action")
RESERVED_REQUEST_KEYS = (*REQUEST_TYPE_KEYS, "request_id", "params")


def _to_builtin_json(value):
    """Convert custom data structures to JSON-serializable builtins at I/O boundaries."""
    if isinstance(value, HashTable):
        converted = {}
        for key in value:
            converted[key] = _to_builtin_json(value[key])
        return converted
    if isinstance(value, ArrayList):
        converted = []
        for item in value:
            converted.append(_to_builtin_json(item))
        return converted
    if isinstance(value, tuple):
        converted = []
        for item in value:
            converted.append(_to_builtin_json(item))
        return converted
    if isinstance(value, list):
        converted = []
        for item in value:
            converted.append(_to_builtin_json(item))
        return converted
    if isinstance(value, dict):
        converted = {}
        for key, item in value.items():
            converted[key] = _to_builtin_json(item)
        return converted
    return value


class PlatformServer:
    def __init__(self, players_per_match=DEFAULT_PLAYERS_PER_MATCH, game_servers=None):
        self.accounts = Accounts()
        self.matchmaking = Matchmaking()
        self.leaderboard = Leaderboard()
        self.history = History()
        self.catalog = Catalog()
        self.chat = Chat()
        self.games = GameRegistry(game_servers)
        self.game_connector = GameConnector(self.games)
        game_names = ArrayList()
        for game_name in self.games.game_servers:
            game_names.append(game_name)
        self.ratings = Ratings(game_names)
        self._ratings_loaded_from_file = False
        self._leaderboards_loaded_from_file = False
        self.players_per_match = players_per_match
        self.max_players_per_instance = DEFAULT_MAX_PLAYERS_PER_INSTANCE
        self.next_game_id = 1
        self.active_game_id = None
        self.instance_player_counts = HashTable()  # game_id -> int player count (compat mirror)
        self.instance_players = HashTable()  # game_id -> HashTable(username -> True)
        self.pending_matches = HashTable()  # username -> game_id, cleared when player acknowledges
        # Separate leaderboards/counters per game + stat.
        # Example board names: "ellie:deaths", "deven:disconnects", "global:score".
        self.game_leaderboards = HashTable()
        self.game_counters = HashTable()

        self.data_ingest = DataIngest(self.accounts, self.leaderboard, self.catalog)
        self.data_ingest.load_data()
        self._leaderboards_loaded_from_file = self._load_leaderboard_state()
        self._ratings_loaded_from_file = self._load_ratings_state()
        self._load_runtime_state()

        # Build player search index from all loaded accounts
        self.player_search = PlayerSearch()
        for username in self.accounts.accounts:
            account = self.accounts.get_account(username)
            if account:
                profile = HashTable()
                profile["name"] = account.username
                profile["total_play_time"] = account.minutes_played
                profile["games_played"] = 0
                profile["win_rate"] = 0.0
                profile["favorite_game"] = account.favorite_game
                profile["messages_sent"] = account.messages_sent
                profile["avatar"] = int(getattr(account, "avatar", 1) or 1)
                self.player_search.register(username, username, profile)

    def _sync_player_search_profile(self, username):
        """Refresh one player's searchable profile from account data."""
        account = self.accounts.get_account(username)
        if not account:
            return
        profile = HashTable()
        profile["name"] = account.username
        profile["total_play_time"] = account.minutes_played
        profile["games_played"] = self._get_counter_value("global:sessions", username)
        profile["win_rate"] = 0.0
        profile["favorite_game"] = account.favorite_game
        profile["messages_sent"] = account.messages_sent
        profile["avatar"] = int(getattr(account, "avatar", 1) or 1)
        self.player_search.register(username, username, profile)

    def _serialize_game_counters(self):
        data = HashTable()
        for board_name in self.game_counters:
            counters = self.game_counters[board_name]
            data[board_name] = HashTable()
            for username in counters:
                data[board_name][username] = counters[username]
        return data

    def _serialize_history(self):
        data = HashTable()
        for username in self.history.history:
            matches = self.history.history[username]
            rows = ArrayList()
            i = 0
            while i < len(matches):
                match = matches[i]
                row = HashTable()
                row["game_id"] = match.game_id
                row["players"] = tuple(match.players)
                row["winner"] = match.winner
                row["score"] = match.score
                row["duration"] = match.duration
                row["ended_at"] = match.ended_at
                row["game_name"] = getattr(match, "game_name", "global")
                rows.append(
                    row
                )
                i += 1
            data[username] = tuple(rows)
        return data

    def _save_runtime_state(self):
        payload = HashTable()
        payload["next_game_id"] = self.next_game_id
        payload["active_game_id"] = self.active_game_id
        payload["instance_player_counts"] = self.instance_player_counts
        payload["instance_players"] = self._serialize_instance_players()
        payload["game_counters"] = self._serialize_game_counters()
        payload["history"] = self._serialize_history()
        # Persist ratings so they survive server restarts
        payload["ratings"] = self._serialize_ratings()
        try:
            with open(RUNTIME_STATE_FILE, "w", encoding="utf-8") as file:
                json.dump(_to_builtin_json(payload), file, indent=2)
        except Exception as error:
            print(f"[platform] Could not save runtime state: {error}")
        self._save_leaderboard_state()
        self._save_ratings_state()

    def _serialize_leaderboard(self, board):
        rows = HashTable()
        for username in board._entries:
            entry = board._entries[username]
            rows[username] = int(entry.score)
        return rows

    def _save_leaderboard_state(self):
        payload = HashTable()
        payload["global_leaderboard"] = self._serialize_leaderboard(self.leaderboard)
        payload["game_leaderboards"] = HashTable()
        for board_name in self.game_leaderboards:
            payload["game_leaderboards"][board_name] = self._serialize_leaderboard(self.game_leaderboards[board_name])
        payload["game_counters"] = self._serialize_game_counters()
        try:
            with open(LEADERBOARD_STATE_FILE, "w", encoding="utf-8") as file:
                json.dump(_to_builtin_json(payload), file, indent=2)
        except Exception as error:
            print(f"[platform] Could not save leaderboard state: {error}")

    def _load_leaderboard_state(self):
        if not LEADERBOARD_STATE_FILE.exists():
            return False
        try:
            with open(LEADERBOARD_STATE_FILE, "r", encoding="utf-8") as file:
                payload = json.load(file)
        except Exception as error:
            print(f"[platform] Could not load leaderboard state: {error}")
            return False

        self.leaderboard = Leaderboard()
        self.game_leaderboards = HashTable()
        self.game_counters = HashTable()
        loaded_any = False

        for username, score in payload.get("global_leaderboard", {}).items():
            self.leaderboard.add_score(username, int(score))
            loaded_any = True

        for board_name, entries in payload.get("game_leaderboards", {}).items():
            board = Leaderboard()
            for username, score in entries.items():
                board.add_score(username, int(score))
                loaded_any = True
            self.game_leaderboards[board_name] = board

        for board_name, raw_counter in payload.get("game_counters", {}).items():
            counters = HashTable()
            for username, score in raw_counter.items():
                counters[username] = int(score)
                loaded_any = True
            self.game_counters[board_name] = counters

        return loaded_any

    def _serialize_ratings(self):
        """Convert ratings to a plain dict: {game_name: [score, score, ...]}"""
        data = HashTable()
        for game_name in self.ratings.game_ratings:
            gr = self.ratings.game_ratings[game_name]
            scores = ArrayList()
            for s in gr.scores:
                scores.append(s)
            data[game_name] = scores
        return data

    def _save_ratings_state(self):
        """Persist ratings independently from runtime occupancy/history state."""
        payload = self._serialize_ratings()
        try:
            with open(RATINGS_STATE_FILE, "w", encoding="utf-8") as file:
                json.dump(_to_builtin_json(payload), file, indent=2)
        except Exception as error:
            print(f"[platform] Could not save ratings state: {error}")

    def _load_ratings_state(self):
        """Load ratings from dedicated ratings_data.json if present."""
        if not RATINGS_STATE_FILE.exists():
            return False
        try:
            with open(RATINGS_STATE_FILE, "r", encoding="utf-8") as file:
                payload = json.load(file)
        except Exception as error:
            print(f"[platform] Could not load ratings state: {error}")
            return False
        loaded_any = False
        for game_name, scores in payload.items():
            for stars in scores:
                try:
                    self.ratings.rate(game_name, int(stars))
                    loaded_any = True
                except Exception:
                    pass
        return loaded_any

    def _load_runtime_state(self):
        if not RUNTIME_STATE_FILE.exists():
            return
        try:
            with open(RUNTIME_STATE_FILE, "r", encoding="utf-8") as file:
                payload = json.load(file)
        except Exception as error:
            print(f"[platform] Could not load runtime state: {error}")
            return

        self.next_game_id = int(payload.get("next_game_id", self.next_game_id))
        active_game_id = payload.get("active_game_id")
        self.active_game_id = int(active_game_id) if active_game_id is not None else None

        raw_counts = payload.get("instance_player_counts", {})
        self.instance_player_counts = HashTable()
        for game_id, count in raw_counts.items():
            self.instance_player_counts[int(game_id)] = int(count)

        self.instance_players = HashTable()
        raw_players = payload.get("instance_players", {})
        if not raw_players:
            # Older runtime snapshots tracked only aggregate counts, which drift over time.
            # Reset occupancy state so connection status is rebuilt from live matches.
            self.instance_player_counts = HashTable()
            self.active_game_id = None
        for game_id, usernames in raw_players.items():
            members = HashTable()
            for username in usernames:
                members[username] = True
            self.instance_players[int(game_id)] = members

        # Restore per-board counters and rebuild corresponding leaderboard entries
        # only when dedicated leaderboard state file was not loaded.
        if not self._leaderboards_loaded_from_file:
            self.game_counters = HashTable()
            self.game_leaderboards = HashTable()
            for board_name, raw_counter in payload.get("game_counters", {}).items():
                counters = HashTable()
                for username, score in raw_counter.items():
                    numeric_score = int(score)
                    counters[username] = numeric_score
                    self._set_board_score(board_name, username, numeric_score)
                self.game_counters[board_name] = counters

        # Restore match history.
        for username, matches in payload.get("history", {}).items():
            for match in matches:
                self.history.add_match(
                    match.get("game_id"),
                    match.get("players", ()),
                    match.get("winner"),
                    score=match.get("score", 0),
                    duration=match.get("duration", 0),
                    ended_at=match.get("ended_at"),
                    game_name=match.get("game_name", "global"),
                )

        # Restore ratings from runtime_state only if dedicated ratings file was not loaded.
        if not self._ratings_loaded_from_file:
            for game_name, scores in payload.get("ratings", {}).items():
                for stars in scores:
                    try:
                        self.ratings.rate(game_name, int(stars))
                    except Exception:
                        pass

    def register(self, username, password):
        result = self.accounts.register(username, password)
        # Add new player to search index when they register
        if result:
            profile = HashTable()
            profile["name"] = username
            profile["total_play_time"] = 0
            profile["games_played"] = 0
            profile["win_rate"] = 0.0
            profile["favorite_game"] = ""
            profile["messages_sent"] = 0
            profile["avatar"] = 1
            self.player_search.register(username, username, profile)
            self._save_runtime_state()
        return result

    def login(self, username, password):
        return self.accounts.login(username, password)

    def join_queue(self, username, game="global"):
        if not self.accounts.exists(username):
            return False
        self.matchmaking.join_queue(username, game)
        return True

    def try_create_match(self, username=None, game="global"):
        # If this player already has a pending match, return it
        if username and username in self.pending_matches:
            game_id = self.pending_matches[username]
            match_data = HashTable()
            match_data["game_id"] = game_id
            one_player = ArrayList()
            one_player.append(username)
            match_data["players"] = tuple(one_player)
            return match_data

        players = self.matchmaking.match_players(self.players_per_match, game)
        if len(players) == 0:
            return None
        game_id = self._get_or_create_available_instance(len(players))
        self._add_players_to_instance(game_id, players)
        # store pending match for every matched player so all their polls succeed
        for p in players:
            self.pending_matches[p] = game_id
        self._save_runtime_state()
        match_data = HashTable()
        match_data["game_id"] = game_id
        match_data["players"] = tuple(players)
        return match_data

    def acknowledge_match(self, username):
        """Call after a client has received and stored the match — clears the pending entry."""
        if username in self.pending_matches:
            self.pending_matches.remove(username)

    def _get_or_create_available_instance(self, incoming_players):
        """
        Reuse current instance until it reaches max capacity, then open new one.
        """
        if self.active_game_id is not None:
            current_count = self._get_instance_player_count(self.active_game_id)
            if current_count + incoming_players <= self.max_players_per_instance:
                return self.active_game_id

        game_id = self.next_game_id
        self.next_game_id += 1
        self.chat.start_session(game_id)
        self.instance_players[game_id] = HashTable()
        self.instance_player_counts[game_id] = 0
        self.active_game_id = game_id
        return game_id

    def _get_game_popularity(self, game_name):
        board_name = f"{game_name}:sessions"
        if board_name not in self.game_counters:
            return 0
        counters = self.game_counters[board_name]
        total = 0
        for username in counters:
            total += int(counters[username])
        return total

    def _get_game_rating(self, game_name):
        if game_name not in self.ratings.game_ratings:
            return 0.0
        return float(self.ratings.game_ratings[game_name].average())

    def list_games(self, sort_by="popularity", descending=True):
        """
        Return game catalog sorted for concrete platform use-cases:
        - popularity: total completed sessions per game
        - rating: average stars
        - recency: most recently registered game first
        """
        rows = ArrayList()
        for game in self.games.list_games():
            row = HashTable()
            row["name"] = game["name"]
            row["host"] = game["host"]
            row["port"] = game["port"]
            row["popularity"] = self._get_game_popularity(game["name"])
            row["rating"] = self._get_game_rating(game["name"])
            row["recency"] = int(game.get("added_order", 0))
            rows.append(row)

        if sort_by == "rating":
            key_fn = lambda row: (row["rating"], row["name"])
        elif sort_by == "recency":
            key_fn = lambda row: (row["recency"], row["name"])
        else:
            key_fn = lambda row: (row["popularity"], row["name"])

        sorted_rows = insertion_sort(rows, key=key_fn, reverse=bool(descending))
        return tuple(sorted_rows)

    def get_game_server(self, game):
        return self.games.get_game(game)

    def send_game_request(self, game, request):
        return self.game_connector.send(game, request)

    def send_message(self, game_id, username, text, game="global"):
        allowed = self.chat.send_message(game_id, username, text)
        if not allowed:
            return False
        self.accounts.add_message(username)
        self._increment_board_score(f"{game}:chats", username, 1)
        self._increment_board_score("global:chats", username, 1)
        self._sync_player_search_profile(username)
        self._save_runtime_state()
        return True

    def get_chat(self, game_id):
        # Keep protocol shape, but use HashTable internally.
        messages = self.chat.get_messages(game_id)
        message_rows = ArrayList()
        for message in messages:
            row = HashTable()
            row["sender"] = message.sender
            row["message"] = message.text
            row["time"] = message.timestamp
            message_rows.append(row)
        payload = HashTable()
        payload["messages"] = tuple(message_rows)
        return payload

    def instance_status(self, game_id):
        """
        Return occupancy for a game instance so clients can show X/30 connections.
        """
        current = self._get_instance_player_count(game_id)
        payload = HashTable()
        payload["game_id"] = game_id
        payload["current_players"] = current
        payload["max_players"] = self.max_players_per_instance
        return payload

    def end_game(self, game_id, players, winner, score, game="global", duration=0):
        session_duration = int(duration) if duration is not None else 0
        play_minutes = 0
        if session_duration > 0:
            play_minutes = max(1, int((session_duration + 59) // 60))
        self.history.add_match(
            game_id,
            players,
            winner,
            score=score,
            duration=session_duration,
            game_name=game,
        )
        self.leaderboard.add_score(winner, score)
        self._set_board_score(f"{game}:score", winner, score)
        self._set_board_score("global:score", winner, score)
        for player in players:
            self.record_session_result(
                game=game,
                username=player,
                score=score if player == winner else 0,
                play_time=play_minutes,
            )
        self._remove_players_from_instance(game_id, players)
        self._save_runtime_state()
        return True

    def _serialize_instance_players(self):
        data = HashTable()
        for game_id in self.instance_players:
            members = self.instance_players[game_id]
            usernames = ArrayList()
            for username in members:
                usernames.append(username)
            data[game_id] = tuple(usernames)
        return data

    def _get_instance_player_count(self, game_id):
        if game_id in self.instance_players:
            return len(self.instance_players[game_id])
        if game_id in self.instance_player_counts:
            return int(self.instance_player_counts[game_id])
        return 0

    def _add_players_to_instance(self, game_id, players):
        if game_id not in self.instance_players:
            self.instance_players[game_id] = HashTable()
        members = self.instance_players[game_id]
        for username in players:
            members[username] = True
        self.instance_player_counts[game_id] = len(members)

    def _remove_players_from_instance(self, game_id, players):
        if game_id not in self.instance_players:
            # Fallback for older runtime-state data that only had counts.
            if game_id in self.instance_player_counts:
                current = int(self.instance_player_counts[game_id])
                remaining = current - len(players)
                if remaining <= 0:
                    self.instance_player_counts.remove(game_id)
                    self.chat.end_session(game_id)
                    if self.active_game_id == game_id:
                        self.active_game_id = None
                else:
                    self.instance_player_counts[game_id] = remaining
            return

        members = self.instance_players[game_id]
        for username in players:
            if username in members:
                members.remove(username)

        remaining = len(members)
        self.instance_player_counts[game_id] = remaining
        if remaining <= 0:
            self.instance_players.remove(game_id)
            self.instance_player_counts.remove(game_id)
            self.chat.end_session(game_id)
            if self.active_game_id == game_id:
                self.active_game_id = None

    def _get_or_create_board(self, board_name):
        if board_name not in self.game_leaderboards:
            self.game_leaderboards[board_name] = Leaderboard()
        return self.game_leaderboards[board_name]

    def _get_or_create_board_counter(self, board_name):
        if board_name not in self.game_counters:
            self.game_counters[board_name] = HashTable()
        return self.game_counters[board_name]

    def _set_board_score(self, board_name, username, score):
        board = self._get_or_create_board(board_name)
        board.add_score(username, score)

    def _increment_board_score(self, board_name, username, amount=1):
        counters = self._get_or_create_board_counter(board_name)
        current = counters[username] if username in counters else 0
        new_score = current + amount
        counters[username] = new_score
        self._set_board_score(board_name, username, new_score)
        return new_score

    def _get_counter_value(self, board_name, username):
        counters = self._get_or_create_board_counter(board_name)
        if username not in counters:
            return 0
        return counters[username]

    def record_session_result(
        self,
        game,
        username,
        score=0,
        play_time=0,
        chats_delta=0,
        deaths_delta=0,
        disconnects_delta=0,
    ):
        """
        Update per-game leaderboards after one completed session.
        Tracks raw per-game metrics for games without winner/win-rate concepts.
        """
        if not self.accounts.exists(username):
            return False

        self._set_board_score(f"{game}:score", username, score)
        self._increment_board_score(f"{game}:play_time", username, play_time)
        self._increment_board_score(f"{game}:sessions", username, 1)
        self._increment_board_score("global:sessions", username, 1)
        if chats_delta:
            self._increment_board_score(f"{game}:chats", username, chats_delta)
        if deaths_delta:
            self._increment_board_score(f"{game}:deaths", username, deaths_delta)
        if disconnects_delta:
            self._increment_board_score(f"{game}:disconnects", username, disconnects_delta)
        self._sync_player_search_profile(username)
        self._save_runtime_state()
        return True

    def player_disconnected(self, username, game="global"):
        if not self.accounts.exists(username):
            return False
        self._increment_board_score(f"{game}:disconnects", username, 1)
        self._save_runtime_state()
        return True

    def player_died(self, username, game="global"):
        if not self.accounts.exists(username):
            return False
        self._increment_board_score(f"{game}:deaths", username, 1)
        self._save_runtime_state()
        return True

    def top_players(self, k, game=None, stat=None):
        if game and stat:
            board_name = f"{game}:{stat}"
            if board_name in self.game_leaderboards:
                return self.game_leaderboards[board_name].top_k(k)
            return ArrayList()
        if game:
            board_name = f"{game}:score"
            if board_name in self.game_leaderboards:
                return self.game_leaderboards[board_name].top_k(k)
            return ArrayList()
        return self.leaderboard.top_k(k)

    def player_rank(self, username, game, stat="score"):
        if not self.accounts.exists(username):
            return None
        board_name = f"{game}:{stat}"
        if board_name not in self.game_leaderboards:
            return None
        return self.game_leaderboards[board_name].rank_of(username)

    def players_in_score_range(self, game, stat, low, high):
        board_name = f"{game}:{stat}"
        if board_name not in self.game_leaderboards:
            return ArrayList()
        return self.game_leaderboards[board_name].range_query(low, high)

    def player_history(
        self,
        username,
        sort_by="date",
        descending=True,
        game=None,
        start_date=None,
        end_date=None,
        outcome="all",
    ):
        matches = self.history.get_player_history(
            username,
            sort_by=sort_by,
            descending=descending,
            game=game,
            start_date=start_date,
            end_date=end_date,
            outcome=outcome,
        )
        rows = ArrayList()
        for match in matches:
            row = HashTable()
            row["game_id"] = match.game_id
            row["game_name"] = getattr(match, "game_name", "global")
            row["winner"] = match.winner
            row["score"] = match.score
            row["duration"] = match.duration
            row["ended_at"] = match.ended_at
            row["outcome"] = "win" if str(match.winner) == str(username) else "loss"
            rows.append(row)
        return tuple(rows)

    def search_players(self, prefix):
        """Return list of player profiles whose name starts with prefix."""
        results = ArrayList()
        for profile in self.player_search.search_prefix(prefix):
            results.append(profile)
        return tuple(results)

    def get_player_profile(self, username):
        """Return a single player's full profile by exact username."""
        return self.player_search.get_profile(username)

    # --- Favorite game -----------------------------------------------------

    def set_favorite(self, username, game_id):
        result = self.accounts.set_favorite(username, game_id)
        if result:
            self._sync_player_search_profile(username)
            self._save_runtime_state()
        return result

    def get_favorite(self, username):
        return self.accounts.get_favorite(username)

    # --- Minutes played ----------------------------------------------------

    def add_minutes(self, username, minutes):
        result = self.accounts.add_minutes(username, minutes)
        if result:
            self._sync_player_search_profile(username)
            self._save_runtime_state()
        return result

    def get_minutes(self, username):
        return self.accounts.get_minutes(username)

    # --- Messages sent -----------------------------------------------------

    def get_messages_sent(self, username):
        return self.accounts.get_messages_sent(username)

    def rate_game(self, game_name, stars):
        self.ratings.rate(game_name, int(stars))
        self._save_runtime_state()
        return True

    def get_rating_rankings(self):
        return self.ratings.get_rankings()

    def get_highest_rated_game(self):
        return self.ratings.get_highest_rated()

    def get_lowest_rated_game(self):
        return self.ratings.get_lowest_rated()
    
    def get_player_stats(self, username):
        if not self.accounts.exists(username):
            return None
        games_played = self._get_counter_value("global:sessions", username)
        minutes = self.accounts.get_minutes(username)
        messages = self.accounts.get_messages_sent(username)
        favorite = self.accounts.get_favorite(username)
        result = HashTable()
        result["games_played"] = games_played
        result["minutes_played"] = int(minutes) if minutes else 0
        result["messages_sent"] = int(messages) if messages else 0
        result["favorite_game"] = favorite or ""
        return result

    def set_avatar(self, username, avatar_num):
        result = self.accounts.set_avatar(username, avatar_num)
        if result:
            self._sync_player_search_profile(username)
            self._save_runtime_state()
        return result

    def get_avatar(self, username):
        return self.accounts.get_avatar(username)
    
class GameRegistry:
    def __init__(self, game_servers=None):
        self.game_servers = HashTable()
        self._next_added_order = 1
        for name, host, port in game_servers or ():
            self.add_game(name, host, port)

    def add_game(self, name, host, port):
        if not name:
            raise ValueError("game name is required")
        game = HashTable()
        game["name"] = name
        game["host"] = host
        game["port"] = int(port)
        game["added_order"] = self._next_added_order
        self._next_added_order += 1
        self.game_servers[name] = game

    def list_games(self):
        games = ArrayList()
        for name in self.game_servers:
            game = self.game_servers[name]
            row = HashTable()
            row["name"] = game["name"]
            row["host"] = game["host"]
            row["port"] = game["port"]
            row["added_order"] = game.get("added_order", 0)
            games.append(row)
        return tuple(games)

    def get_game(self, name):
        game = self.game_servers.get(name)
        if game is None:
            raise ValueError(f"unknown game: {name}")
        return game


class GameConnector:
    def __init__(self, games, timeout=5):
        self.games = games
        self.timeout = timeout

    def send(self, game_name, request):
        game = self.games.get_game(game_name)
        message = json.dumps(request).encode("utf-8") + b"\n"
        with socket.create_connection((game["host"], game["port"]), timeout=self.timeout) as connection:
            connection.sendall(message)
            response = self.read_line(connection)
        if response == "":
            return None
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return response

    def read_line(self, connection):
        chunks = ArrayList()
        while True:
            chunk = connection.recv(1)
            if not chunk or chunk == b"\n":
                break
            chunks.append(chunk)
        return b"".join(chunks).decode("utf-8")


class RequestDispatcher:
    allowed_methods = ArrayList()
    allowed_methods.append("register")
    allowed_methods.append("login")
    allowed_methods.append("join_queue")
    allowed_methods.append("try_create_match")
    allowed_methods.append("acknowledge_match")
    allowed_methods.append("list_games")
    allowed_methods.append("get_game_server")
    allowed_methods.append("send_game_request")
    allowed_methods.append("send_message")
    allowed_methods.append("get_chat")
    allowed_methods.append("instance_status")
    allowed_methods.append("end_game")
    allowed_methods.append("top_players")
    allowed_methods.append("player_history")
    allowed_methods.append("set_favorite")
    allowed_methods.append("get_favorite")
    allowed_methods.append("add_minutes")
    allowed_methods.append("get_minutes")
    allowed_methods.append("get_messages_sent")
    allowed_methods.append("player_disconnected")
    allowed_methods.append("player_died")
    allowed_methods.append("record_session_result")
    allowed_methods.append("player_rank")
    allowed_methods.append("players_in_score_range")
    allowed_methods.append("rate_game")
    allowed_methods.append("get_rating_rankings")
    allowed_methods.append("get_highest_rated_game")
    allowed_methods.append("get_lowest_rated_game")
    allowed_methods.append("search_players")
    allowed_methods.append("get_player_profile")
    allowed_methods.append("get_player_stats")
    allowed_methods.append("set_avatar")
    allowed_methods.append("get_avatar")

    def __init__(self, platform):
        self.platform = platform
        self.lock = threading.RLock()

    def dispatch(self, request):
        if not isinstance(request, dict):
            raise ValueError("request must be a JSON object")
        request_type = self.get_request_type(request)
        if request_type not in self.allowed_methods:
            raise ValueError(f"unknown request type: {request_type}")
        params = self.get_params(request)
        method = getattr(self.platform, request_type)
        with self.lock:
            return method(**params)

    def get_request_type(self, request):
        for key in REQUEST_TYPE_KEYS:
            request_type = request.get(key)
            if request_type:
                return request_type
        return None

    def get_params(self, request):
        params = request.get("params")
        if params is None:
            params = HashTable()
            for key, value in request.items():
                if key not in RESERVED_REQUEST_KEYS:
                    params[key] = value
        if not isinstance(params, dict):
            if isinstance(params, HashTable):
                converted = {}
                for key in params:
                    converted[key] = params[key]
                return converted
            raise ValueError("params must be a JSON object")
        return params


class ThreadedPlatformTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address, handler_class, dispatcher):
        super().__init__(address, handler_class)
        self.dispatcher = dispatcher


class PlatformRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        for raw_line in self.rfile:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            response = self.handle_request_line(raw_line)
            self.wfile.write(json.dumps(_to_builtin_json(response), default=str).encode("utf-8") + b"\n")

    def handle_request_line(self, raw_line):
        request_id = None
        try:
            request = json.loads(raw_line.decode("utf-8"))
            if isinstance(request, dict):
                request_id = request.get("request_id")
            result = self.server.dispatcher.dispatch(request)
            return {"ok": True, "request_id": request_id, "result": result}
        except json.JSONDecodeError as error:
            return {"ok": False, "request_id": request_id, "error": f"invalid JSON: {error.msg}"}
        except TypeError as error:
            return {"ok": False, "request_id": request_id, "error": f"bad request parameters: {error}"}
        except Exception as error:
            return {"ok": False, "request_id": request_id, "error": str(error)}


def run_server(host=DEFAULT_HOST, port=DEFAULT_PORT, players_per_match=DEFAULT_PLAYERS_PER_MATCH, game_servers=None):
    platform = PlatformServer(players_per_match=players_per_match, game_servers=game_servers)
    dispatcher = RequestDispatcher(platform)
    with ThreadedPlatformTCPServer((host, port), PlatformRequestHandler, dispatcher) as server:
        print(f"Platform server listening on {host}:{port}")
        server.serve_forever()


def parse_args():
    parser = argparse.ArgumentParser(description="Run the platform server.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", default=DEFAULT_PORT, type=int)
    parser.add_argument("--players-per-match", default=DEFAULT_PLAYERS_PER_MATCH, type=int)
    parser.add_argument("--game-server", action="append", default=[])
    parser.add_argument("--game-port", action="append", default=[], type=int)
    parser.add_argument("--game-host", default=DEFAULT_GAME_HOST)
    return parser.parse_args()


def parse_game_servers(named_servers, ports, default_host):
    game_servers = ArrayList()
    for item in parse_named_game_servers(GAME_SERVER_ENV):
        game_servers.append(item)
    for item in parse_named_game_servers(",".join(named_servers)):
        game_servers.append(item)
    for index, port in enumerate(ports, start=1):
        game_servers.append((f"game{index}", default_host, port))
    return tuple(game_servers)


def parse_named_game_servers(raw_value):
    game_servers = ArrayList()
    for item in raw_value.split(","):
        item = item.strip()
        if not item:
            continue
        name, address = item.split("=", 1)
        host, port = address.rsplit(":", 1)
        game_servers.append((name.strip(), host.strip(), int(port)))
    return tuple(game_servers)


if __name__ == "__main__":
    args = parse_args()
    game_servers = parse_game_servers(args.game_server, args.game_port, args.game_host)
    run_server(host=args.host, port=args.port, players_per_match=args.players_per_match, game_servers=game_servers)
