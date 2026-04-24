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
from platform_server.ratings import Ratings


DEFAULT_HOST = os.getenv("PLATFORM_SERVER_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("PLATFORM_SERVER_PORT", "50072"))
DEFAULT_PLAYERS_PER_MATCH = int(os.getenv("PLATFORM_PLAYERS_PER_MATCH", "2"))
DEFAULT_GAME_HOST = os.getenv("PLATFORM_GAME_HOST", "127.0.0.1")
GAME_SERVER_ENV = os.getenv("PLATFORM_GAME_SERVERS", "")

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
        self.next_game_id = 1
        self.active_game_id = None

        self.data_ingest = DataIngest(self.accounts, self.leaderboard, self.catalog)
        self.data_ingest.load_data()

    def register(self, username, password):
        return self.accounts.register(username, password)

    def login(self, username, password):
        return self.accounts.login(username, password)

    def join_queue(self, username):
        if not self.accounts.exists(username):
            return False
        self.matchmaking.join_queue(username)
        return True

    def try_create_match(self):
        players = self.matchmaking.match_players(1)
        if len(players) == 0:
            return None
        if self.active_game_id is not None:
            game_id = self.active_game_id
        else:
            game_id = self.next_game_id
            self.next_game_id += 1
            self.chat.start_session(game_id)
            self.active_game_id = game_id
        return {"game_id": game_id, "players": players}

    def list_games(self):
        return self.games.list_games()

    def get_game_server(self, game):
        return self.games.get_game(game)

    def send_game_request(self, game, request):
        return self.game_connector.send(game, request)

    def send_message(self, game_id, username, text):
        self.chat.send_message(game_id, username, text)
        # Track message count per user
        self.accounts.add_message(username)
        return True

    def get_chat(self, game_id):
        return self.chat.get_messages(game_id)

    def end_game(self, game_id, players, winner, score):
        self.history.add_match(game_id, players, winner)
        self.leaderboard.add_score(winner, score)
        self.chat.end_session(game_id)
        if self.active_game_id == game_id:
            self.active_game_id = None
        return True

    def top_players(self, k):
        return self.leaderboard.top_k(k)

    def player_history(self, username):
        return self.history.get_player_history(username)

    # --- Favorite game -----------------------------------------------------

    def set_favorite(self, username, game_id):
        return self.accounts.set_favorite(username, game_id)

    def get_favorite(self, username):
        return self.accounts.get_favorite(username)

    # --- Minutes played ----------------------------------------------------

    def add_minutes(self, username, minutes):
        return self.accounts.add_minutes(username, minutes)

    def get_minutes(self, username):
        return self.accounts.get_minutes(username)

    # --- Messages sent -----------------------------------------------------

    def get_messages_sent(self, username):
        return self.accounts.get_messages_sent(username)

    def rate_game(self, game_name, stars):
        self.ratings.rate(game_name, int(stars))
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
        "send_message", "get_chat", "end_game", "top_players",
        "player_history", "set_favorite", "get_favorite",
        "add_minutes", "get_minutes", "get_messages_sent",
        "rate_game", "get_rating_rankings", "get_highest_rated_game", "get_lowest_rated_game",
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