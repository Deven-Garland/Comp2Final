"""
connection.py - Client connection to the platform server

Matches the new server protocol: newline-delimited JSON over TCP.

Author: Team MOSFET
Date: Spring 2026
Lab: Final Project
"""

import json
import socket
import threading
from datastructures.array import ArrayList
from datastructures.hash_table import HashTable


class ServerConnection:
    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self._sock = None
        self._file = None
        self._lock = threading.Lock()
        self._username = None
        self._session_id = None

    def _payload(self, pairs=()):
        payload = HashTable()
        for key, value in pairs:
            payload[key] = value
        return payload

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(5)
        self._sock.connect((self.host, self.port))
        self._sock.settimeout(None)
        self._file = self._sock.makefile("r")

    def disconnect(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None
            self._file = None

    def ensure_connected(self):
        """Reconnect if the socket is dead."""
        if self._sock is None:
            self.connect()

    def _request(self, action, payload=None):
        if payload is None:
            payload = HashTable()
        request = HashTable()
        request["action"] = action
        for key in payload:
            request[key] = payload[key]
        request_json = {}
        for key in request:
            request_json[key] = request[key]
        with self._lock:
            self._sock.sendall((json.dumps(request_json) + "\n").encode("utf-8"))
            line = self._file.readline()
        if not line:
            response = HashTable()
            response["status"] = "error"
            response["message"] = "No response from server"
            return response
        resp = json.loads(line.strip())
        if "ok" in resp:
            if resp["ok"]:
                response = HashTable()
                response["status"] = "ok"
                response["data"] = resp.get("result", HashTable())
                return response
            else:
                response = HashTable()
                response["status"] = "error"
                response["message"] = resp.get("error", "Unknown error")
                return response
        return resp

    # --- Auth --------------------------------------------------------------

    def login(self, username, password):
        self.ensure_connected()
        resp = self._request("login", self._payload((("username", username), ("password", password))))
        if resp.get("status") == "ok":
            self._username = username
        return resp

    def register(self, username, password, email=None):
        self.ensure_connected()
        resp = self._request("register", self._payload((("username", username), ("password", password))))
        if resp.get("status") == "ok":
            self._username = username
        return resp

    def logout(self):
        self._username = None

    # --- Game list ---------------------------------------------------------

    def get_game_list(self):
        resp = self._request("list_games")
        if resp.get("status") == "ok":
            return resp.get("data") or ArrayList()
        return ArrayList()

    def get_game_list_sorted(self, sort_by="popularity", descending=True):
        payload = self._payload((("sort_by", sort_by), ("descending", bool(descending))))
        resp = self._request("list_games", payload)
        if resp.get("status") == "ok":
            return resp.get("data") or ArrayList()
        return ArrayList()

    # --- Stats -------------------------------------------------------------

    def get_leaderboard(self, top_n=10):
        return self._request("top_players", self._payload((("k", top_n),)))

    def get_game_leaderboard(self, game, stat="score", top_n=10):
        return self._request("top_players", self._payload((("k", top_n), ("game", game), ("stat", stat))))

    def get_player_rank(self, username, game, stat="score"):
        return self._request("player_rank", self._payload((("username", username), ("game", game), ("stat", stat))))

    def get_score_range(self, game, stat, low, high):
        return self._request(
            "players_in_score_range",
            self._payload((("game", game), ("stat", stat), ("low", low), ("high", high))),
        )

    def rate_game(self, game_name, stars):
        return self._request("rate_game", self._payload((("game_name", game_name), ("stars", int(stars)))))

    def get_rating_rankings(self):
        return self._request("get_rating_rankings")

    def get_highest_rated_game(self):
        return self._request("get_highest_rated_game")

    def get_lowest_rated_game(self):
        return self._request("get_lowest_rated_game")

    def get_minutes(self, username):
        resp = self._request("get_minutes", self._payload((("username", username),)))
        if resp.get("status") == "ok":
            return resp.get("data") or 0
        return 0

    def add_minutes(self, username, minutes):
        return self._request("add_minutes", self._payload((("username", username), ("minutes", minutes))))

    def get_messages_sent(self, username):
        resp = self._request("get_messages_sent", self._payload((("username", username),)))
        if resp.get("status") == "ok":
            return resp.get("data") or 0
        return 0

    def get_player_history_sorted(self, username, sort_by="date", descending=True):
        payload = self._payload((
            ("username", username),
            ("sort_by", sort_by),
            ("descending", bool(descending)),
        ))
        resp = self._request("player_history", payload)
        if resp.get("status") == "ok":
            return resp.get("data") or ArrayList()
        return ArrayList()

    def report_disconnect(self, username, game="global"):
        return self._request("player_disconnected", self._payload((("username", username), ("game", game))))

    def report_death(self, username, game="global"):
        return self._request("player_died", self._payload((("username", username), ("game", game))))

    # --- Favorite game -----------------------------------------------------

    def get_favorite(self, username):
        resp = self._request("get_favorite", self._payload((("username", username),)))
        if resp.get("status") == "ok":
            return resp.get("data") or ""
        return ""

    def set_favorite(self, username, game_id):
        return self._request("set_favorite", self._payload((("username", username), ("game_id", game_id))))

    # --- Player search ------------------------------------------------------

    def search_players(self, prefix):
        resp = self._request("search_players", self._payload((("prefix", prefix),)))
        if resp.get("status") == "ok":
            return resp.get("data") or ArrayList()
        return ArrayList()

    def get_player_profile(self, username):
        resp = self._request("get_player_profile", self._payload((("username", username),)))
        if resp.get("status") == "ok":
            return resp.get("data")
        return None

    # --- Matchmaking -------------------------------------------------------

    def join_queue(self, game="global", skill_rating=1000):
        response = self._request("join_queue", self._payload((("username", self._username), ("game", game))))
        if response.get("status") != "ok":
            message = str(response.get("message", ""))
            if "unexpected keyword argument 'game'" in message or "bad request parameters" in message:
                response = self._request("join_queue", self._payload((("username", self._username),)))
        return response

    def leave_queue(self):
        pass

    def poll_match(self):
        resp = self._request("try_create_match")
        if resp.get("status") == "ok":
            data = resp.get("data")
            if data and data.get("game_id"):
                result = HashTable()
                result["session_id"] = data["game_id"]
                return result
        return None

    def set_session(self, session_id):
        try:
            self._session_id = int(session_id)
        except (TypeError, ValueError):
            self._session_id = session_id

    def clear_session(self):
        self._session_id = None

    # --- Chat --------------------------------------------------------------

    def send_chat(self, message, chat_channel=None, game="global", recipient=None):
        game_id = chat_channel if chat_channel else self._session_id
        if game_id is None:
            game_id = "global"
        payload = self._payload((
            ("game_id", game_id),
            ("username", self._username),
            ("text", message),
            ("game", game),
        ))
        return self._request("send_message", payload)

    def poll_chat(self, chat_channel):
        if chat_channel is None:
            chat_channel = "global"
        resp = self._request("get_chat", self._payload((("game_id", chat_channel),)))
        if resp.get("status") == "ok":
            return resp.get("data") or ArrayList()
        return ArrayList()

    def get_instance_status(self, session_id):
        resp = self._request("instance_status", self._payload((("game_id", int(session_id)),)))
        if resp.get("status") == "ok":
            return resp.get("data") or HashTable()
        return HashTable()

    # --- Session -----------------------------------------------------------

    def leave_session(self, session_id):
        pass

    def close(self):
        self.disconnect()