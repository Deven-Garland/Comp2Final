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
from platform_server.player_search import PlayerSearch
from platform_server.ratings import Ratings
from datastructures.hash_table import HashTable


DEFAULT_HOST = os.getenv("PLATFORM_SERVER_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("PLATFORM_SERVER_PORT", "50072"))
DEFAULT_PLAYERS_PER_MATCH = int(os.getenv("PLATFORM_PLAYERS_PER_MATCH", "2"))
DEFAULT_MAX_PLAYERS_PER_INSTANCE = int(os.getenv("PLATFORM_MAX_PLAYERS_PER_INSTANCE", "30"))
DEFAULT_GAME_HOST = os.getenv("PLATFORM_GAME_HOST", "127.0.0.1")
GAME_SERVER_ENV = os.getenv("PLATFORM_GAME_SERVERS", "")
RUNTIME_STATE_FILE = Path(__file__).with_name("runtime_state.json")

REQUEST_TYPE_KEYS = ("type", "action")
RESERVED_REQUEST_KEYS = (*REQUEST_TYPE_KEYS, "request_id", "params")


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
        self.ratings = Ratings(sorted(self.games.game_servers.keys()))
        self.players_per_match = players_per_match
        self.max_players_per_instance = DEFAULT_MAX_PLAYERS_PER_INSTANCE
        self.next_game_id = 1
        self.active_game_id = None
        self.instance_player_counts = {}
        # Separate leaderboards/counters per game + stat.
        # Example board names: "ellie:deaths", "deven:disconnects", "global:score".
        self.game_leaderboards = HashTable()
        self.game_counters = HashTable()

        self.data_ingest = DataIngest(self.accounts, self.leaderboard, self.catalog)
        self.data_ingest.load_data()
        self._load_runtime_state()

        # Build player search index from all loaded accounts
        self.player_search = PlayerSearch()
        for username in self.accounts.accounts:
            account = self.accounts.get_account(username)
            if account:
                profile = {
                    "name": account.username,
                    "total_play_time": account.minutes_played,
                    "games_played": 0,
                    "win_rate": 0.0,
                    "favorite_game": account.favorite_game,
                    "messages_sent": account.messages_sent,
                }
                self.player_search.register(username, username, profile)

    def _serialize_game_counters(self):
        data = {}
        for board_name in self.game_counters:
            counters = self.game_counters[board_name]
            data[board_name] = {}
            for username in counters:
                data[board_name][username] = counters[username]
        return data

    def _serialize_history(self):
        data = {}
        for username in self.history.history:
            matches = self.history.history[username]
            rows = []
            i = 0
            while i < len(matches):
                match = matches[i]
                rows.append(
                    {
                        "game_id": match.game_id,
                        "players": list(match.players),
                        "winner": match.winner,
                    }
                )
                i += 1
            data[username] = rows
        return data

    def _save_runtime_state(self):
        payload = {
            "next_game_id": self.next_game_id,
            "active_game_id": self.active_game_id,
            "instance_player_counts": self.instance_player_counts,
            "game_counters": self._serialize_game_counters(),
            "history": self._serialize_history(),
        }
        try:
            with open(RUNTIME_STATE_FILE, "w", encoding="utf-8") as file:
                json.dump(payload, file, indent=2)
        except Exception as error:
            print(f"[platform] Could not save runtime state: {error}")

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
        self.instance_player_counts = {
            int(game_id): int(count) for game_id, count in raw_counts.items()
        }

        # Restore per-board counters and rebuild corresponding leaderboard entries.
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
                    match.get("players", []),
                    match.get("winner"),
                )

    def register(self, username, password):
        result = self.accounts.register(username, password)
        # Add new player to search index when they register
        if result:
            profile = {
                "name": username,
                "total_play_time": 0,
                "games_played": 0,
                "win_rate": 0.0,
                "favorite_game": "",
                "messages_sent": 0,
            }
            self.player_search.register(username, username, profile)
            self._save_runtime_state()
        return result

    def login(self, username, password):
        return self.accounts.login(username, password)

    def join_queue(self, username):
        if not self.accounts.exists(username):
            return False
        self.matchmaking.join_queue(username)
        return True

    def try_create_match(self):
        players = self.matchmaking.match_players(self.players_per_match)
        if len(players) == 0:
            return None
        game_id = self._get_or_create_available_instance(len(players))
        self.instance_player_counts[game_id] = self.instance_player_counts.get(game_id, 0) + len(players)
        self._save_runtime_state()
        return {"game_id": game_id, "players": players}

    def _get_or_create_available_instance(self, incoming_players):
        """
        Reuse current instance until it reaches max capacity, then open new one.
        """
        if self.active_game_id is not None:
            current_count = self.instance_player_counts.get(self.active_game_id, 0)
            if current_count + incoming_players <= self.max_players_per_instance:
                return self.active_game_id

        game_id = self.next_game_id
        self.next_game_id += 1
        self.chat.start_session(game_id)
        self.instance_player_counts[game_id] = 0
        self.active_game_id = game_id
        return game_id

    def list_games(self):
        return self.games.list_games()

    def get_game_server(self, game):
        return self.games.get_game(game)

    def send_game_request(self, game, request):
        return self.game_connector.send(game, request)

    def send_message(self, game_id, username, text, game="global"):
        self.chat.send_message(game_id, username, text)
        self.accounts.add_message(username)
        self._increment_board_score(f"{game}:chats", username, 1)
        self._increment_board_score("global:chats", username, 1)
        self._save_runtime_state()
        return True

    def get_chat(self, game_id):
        # FIX: return proper dicts so the client can read sender/message/time
        messages = self.chat.get_messages(game_id)
        return {
            "messages": [
                {"sender": m.sender, "message": m.text, "time": m.timestamp}
                for m in messages
            ]
        }

    def instance_status(self, game_id):
        """
        Return occupancy for a game instance so clients can show X/30 connections.
        """
        current = self.instance_player_counts.get(game_id, 0)
        return {
            "game_id": game_id,
            "current_players": current,
            "max_players": self.max_players_per_instance,
        }

    def end_game(self, game_id, players, winner, score, game="global"):
        self.history.add_match(game_id, players, winner)
        self.leaderboard.add_score(winner, score)
        self._set_board_score(f"{game}:score", winner, score)
        self._set_board_score("global:score", winner, score)
        for player in players:
            self.record_session_result(
                game=game,
                username=player,
                score=score if player == winner else 0,
                play_time=0,
            )
        if game_id in self.instance_player_counts:
            remaining = self.instance_player_counts.get(game_id, 0) - len(players)
            if remaining <= 0:
                self.instance_player_counts.pop(game_id, None)
                self.chat.end_session(game_id)
                if self.active_game_id == game_id:
                    self.active_game_id = None
            else:
                self.instance_player_counts[game_id] = remaining
        self._save_runtime_state()
        return True

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
        if chats_delta:
            self._increment_board_score(f"{game}:chats", username, chats_delta)
        if deaths_delta:
            self._increment_board_score(f"{game}:deaths", username, deaths_delta)
        if disconnects_delta:
            self._increment_board_score(f"{game}:disconnects", username, disconnects_delta)
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
            return []
        if game:
            board_name = f"{game}:score"
            if board_name in self.game_leaderboards:
                return self.game_leaderboards[board_name].top_k(k)
            return []
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
            return []
        return self.game_leaderboards[board_name].range_query(low, high)

    def player_history(self, username):
        return self.history.get_player_history(username)

    def search_players(self, prefix):
        """Return list of player profiles whose name starts with prefix."""
        return self.player_search.search_prefix(prefix)

    def get_player_profile(self, username):
        """Return a single player's full profile by exact username."""
        return self.player_search.get_profile(username)

    # --- Favorite game -----------------------------------------------------

    def set_favorite(self, username, game_id):
        result = self.accounts.set_favorite(username, game_id)
        if result:
            self._save_runtime_state()
        return result

    def get_favorite(self, username):
        return self.accounts.get_favorite(username)

    # --- Minutes played ----------------------------------------------------

    def add_minutes(self, username, minutes):
        result = self.accounts.add_minutes(username, minutes)
        if result:
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


class GameRegistry:
    def __init__(self, game_servers=None):
        self.game_servers = {}
        for name, host, port in game_servers or []:
            self.add_game(name, host, port)

    def add_game(self, name, host, port):
        if not name:
            raise ValueError("game name is required")
        self.game_servers[name] = {"name": name, "host": host, "port": int(port)}

    def list_games(self):
        return list(self.game_servers.values())

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
        chunks = []
        while True:
            chunk = connection.recv(1)
            if not chunk or chunk == b"\n":
                break
            chunks.append(chunk)
        return b"".join(chunks).decode("utf-8")


class RequestDispatcher:
    allowed_methods = (
        "register", "login", "join_queue", "try_create_match",
        "list_games", "get_game_server", "send_game_request",
        "send_message", "get_chat", "instance_status", "end_game", "top_players",
        "player_history", "set_favorite", "get_favorite",
        "add_minutes", "get_minutes", "get_messages_sent",
        "player_disconnected", "player_died",
        "record_session_result", "player_rank", "players_in_score_range",
        "rate_game", "get_rating_rankings", "get_highest_rated_game", "get_lowest_rated_game",
        "search_players", "get_player_profile",
    )

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
            params = {k: v for k, v in request.items() if k not in RESERVED_REQUEST_KEYS}
        if not isinstance(params, dict):
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
            self.wfile.write(json.dumps(response, default=str).encode("utf-8") + b"\n")

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
    game_servers = parse_named_game_servers(GAME_SERVER_ENV)
    game_servers.extend(parse_named_game_servers(",".join(named_servers)))
    for index, port in enumerate(ports, start=1):
        game_servers.append((f"game{index}", default_host, port))
    return game_servers


def parse_named_game_servers(raw_value):
    game_servers = []
    for item in raw_value.split(","):
        item = item.strip()
        if not item:
            continue
        name, address = item.split("=", 1)
        host, port = address.rsplit(":", 1)
        game_servers.append((name.strip(), host.strip(), int(port)))
    return game_servers


if __name__ == "__main__":
    args = parse_args()
    game_servers = parse_game_servers(args.game_server, args.game_port, args.game_host)
    run_server(host=args.host, port=args.port, players_per_match=args.players_per_match, game_servers=game_servers)