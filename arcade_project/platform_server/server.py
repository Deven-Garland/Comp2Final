# Platform server (you implement).
"""
chat.py - Per-game-session chat system

Handles chat messages for each game session on the platform. Each active
game session has its own chat history stored in a circular buffer, so
players only see messages from the game they are currently in.

We use a HashTable to map game_id -> CircularBuffer, so looking up a
specific game's chat is O(1). Each buffer only stores the most recent
messages (default 20), older messages get dropped automatically once
the buffer fills up.

Author: Mennah Khaled Dewidar
Date: [4/18/2026]
Lab: Final Project - Server
"""
"""
server.py - Runtime entrypoint for the arcade platform server.
"""

import argparse
import json
import os
import socketserver
import threading

from platform_server.accounts import Accounts
from platform_server.catalog import Catalog
from platform_server.chat import Chat
from platform_server.data_ingest import DataIngest
from platform_server.history import History
from platform_server.leaderboard import Leaderboard
from platform_server.matchmaking import Matchmaking


DEFAULT_HOST = os.getenv("PLATFORM_SERVER_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("PLATFORM_SERVER_PORT", "5000"))
DEFAULT_PLAYERS_PER_MATCH = int(os.getenv("PLATFORM_PLAYERS_PER_MATCH", "2"))
REQUEST_TYPE_KEYS = ("type", "action")
RESERVED_REQUEST_KEYS = (*REQUEST_TYPE_KEYS, "request_id")


class PlatformServer:
    def __init__(self, players_per_match=DEFAULT_PLAYERS_PER_MATCH):
        self.accounts = Accounts()
        self.matchmaking = Matchmaking()
        self.leaderboard = Leaderboard()
        self.history = History()
        self.catalog = Catalog()
        self.chat = Chat()
        self.players_per_match = players_per_match

        self.data_ingest = DataIngest(self.accounts, self.leaderboard, self.catalog)
        self.data_ingest.load_data()

        self.next_game_id = 1

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
        players = self.matchmaking.match_players(self.players_per_match)

        if len(players) == 0:
            return None

        game_id = self.next_game_id
        self.next_game_id += 1

        self.chat.start_session(game_id)

        return game_id, players

    def send_message(self, game_id, username, text):
        self.chat.send_message(game_id, username, text)
        return True

    def get_chat(self, game_id):
        return self.chat.get_messages(game_id)

    def end_game(self, game_id, players, winner, score):
        self.history.add_match(game_id, players, winner)
        self.leaderboard.add_score(winner, score)
        self.chat.end_session(game_id)
        return True

    def top_players(self, k):
        return self.leaderboard.top_k(k)

    def player_history(self, username):
        return self.history.get_player_history(username)


class RequestDispatcher:
    """Dispatches incoming JSON requests to PlatformServer methods."""

    allowed_methods = (
        "register",
        "login",
        "join_queue",
        "try_create_match",
        "send_message",
        "get_chat",
        "end_game",
        "top_players",
        "player_history",
    )

    def __init__(self, platform, allowed_methods=None):
        self.platform = platform
        self.lock = threading.RLock()
        self.allowed_methods = set(allowed_methods or self.allowed_methods)

    def dispatch(self, request):
        if not isinstance(request, dict):
            raise ValueError("request must be a JSON object")

        request_type = self.get_request_type(request)

        if request_type not in self.allowed_methods:
            raise ValueError(f"unknown request type: {request_type}")

        params = request.get("params")

        if params is None:
            params = {
                key: value
                for key, value in request.items()
                if key not in RESERVED_REQUEST_KEYS
            }

        if not isinstance(params, dict):
            raise ValueError("params must be a JSON object")

        method = getattr(self.platform, request_type)

        with self.lock:
            return method(**params)

    def get_request_type(self, request):
        for key in REQUEST_TYPE_KEYS:
            if request.get(key):
                return request[key]

        return None


class ArcadeTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, request_handler_class, dispatcher):
        super().__init__(server_address, request_handler_class)
        self.dispatcher = dispatcher


class ArcadeRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        for raw_line in self.rfile:
            raw_line = raw_line.strip()

            if not raw_line:
                continue

            response = self.handle_line(raw_line)
            self.wfile.write(json.dumps(response).encode("utf-8") + b"\n")

    def handle_line(self, raw_line):
        request_id = None

        try:
            request = json.loads(raw_line.decode("utf-8"))

            if isinstance(request, dict):
                request_id = request.get("request_id")

            result = self.server.dispatcher.dispatch(request)

            return {
                "ok": True,
                "request_id": request_id,
                "result": result,
            }

        except json.JSONDecodeError as error:
            return {
                "ok": False,
                "request_id": request_id,
                "error": f"invalid JSON: {error.msg}",
            }

        except TypeError as error:
            return {
                "ok": False,
                "request_id": request_id,
                "error": f"bad request parameters: {error}",
            }

        except Exception as error:
            return {
                "ok": False,
                "request_id": request_id,
                "error": str(error),
            }


def run_server(
    host=DEFAULT_HOST,
    port=DEFAULT_PORT,
    players_per_match=DEFAULT_PLAYERS_PER_MATCH,
):
    platform = PlatformServer(players_per_match=players_per_match)
    dispatcher = RequestDispatcher(platform)

    with ArcadeTCPServer((host, port), ArcadeRequestHandler, dispatcher) as server:
        print(f"Platform server listening on {host}:{port}")
        server.serve_forever()


def parse_args():
    parser = argparse.ArgumentParser(description="Run the arcade platform server.")

    parser.add_argument("--host", default=DEFAULT_HOST, help="Host/IP to bind.")
    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help="Port to bind.")
    parser.add_argument(
        "--players-per-match",
        default=DEFAULT_PLAYERS_PER_MATCH,
        type=int,
        help="Number of queued players needed to create a match.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_server(args.host, args.port, args.players_per_match)
