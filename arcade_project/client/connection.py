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


class ServerConnection:
    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self._sock = None
        self._file = None
        self._lock = threading.Lock()
        self._username = None
        self._session_id = None  # FIX: actually store session id

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self.host, self.port))
        self._file = self._sock.makefile("r")

    def disconnect(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None
            self._file = None

    def _request(self, action, payload=None):
        if payload is None:
            payload = {}
        request = {"action": action, **payload}
        with self._lock:
            self._sock.sendall((json.dumps(request) + "\n").encode("utf-8"))
            line = self._file.readline()
        if not line:
            return {"status": "error", "message": "No response from server"}
        resp = json.loads(line.strip())
        if "ok" in resp:
            if resp["ok"]:
                return {"status": "ok", "data": resp.get("result", {})}
            else:
                return {"status": "error", "message": resp.get("error", "Unknown error")}
        return resp

    # --- Auth --------------------------------------------------------------

    def login(self, username, password):
        resp = self._request("login", {"username": username, "password": password})
        if resp.get("status") == "ok":
            self._username = username
        return resp

    def register(self, username, password, email=None):
        resp = self._request("register", {"username": username, "password": password})
        if resp.get("status") == "ok":
            self._username = username
        return resp

    def logout(self):
        self._username = None

    # --- Game list ---------------------------------------------------------

    def get_game_list(self):
        resp = self._request("list_games")
        if resp.get("status") == "ok":
            return resp.get("data") or []
        return []

    # --- Stats -------------------------------------------------------------

    def get_leaderboard(self, top_n=10):
        return self._request("top_players", {"k": top_n})

    def rate_game(self, game_name, stars):
        return self._request("rate_game", {"game_name": game_name, "stars": int(stars)})

    def get_rating_rankings(self):
        return self._request("get_rating_rankings")

    def get_highest_rated_game(self):
        return self._request("get_highest_rated_game")

    def get_lowest_rated_game(self):
        return self._request("get_lowest_rated_game")

    def get_minutes(self, username):
        resp = self._request("get_minutes", {"username": username})
        if resp.get("status") == "ok":
            return resp.get("data") or 0
        return 0

    def add_minutes(self, username, minutes):
        return self._request("add_minutes", {"username": username, "minutes": minutes})

    def get_messages_sent(self, username):
        resp = self._request("get_messages_sent", {"username": username})
        if resp.get("status") == "ok":
            return resp.get("data") or 0
        return 0

    # --- Favorite game -----------------------------------------------------

    def get_favorite(self, username):
        resp = self._request("get_favorite", {"username": username})
        if resp.get("status") == "ok":
            return resp.get("data") or ""
        return ""

    def set_favorite(self, username, game_id):
        return self._request("set_favorite", {"username": username, "game_id": game_id})

    # --- Matchmaking -------------------------------------------------------

    def join_queue(self, skill_rating=1000):
        return self._request("join_queue", {"username": self._username})

    def leave_queue(self):
        pass

    def poll_match(self):
        resp = self._request("try_create_match")
        if resp.get("status") == "ok":
            data = resp.get("data")
            if data and data.get("game_id"):
                return {"session_id": data["game_id"]}
        return None

    def set_session(self, session_id):
        """Call this when a match is found so chat knows which session to use."""
        self._session_id = session_id

    def clear_session(self):
        """Call this when leaving a game."""
        self._session_id = None

    # --- Chat --------------------------------------------------------------

    def send_chat(self, message, recipient=None):
        # FIX: _session_id is now properly set via set_session()
        payload = {"game_id": self._session_id, "username": self._username, "text": message}
        return self._request("send_message", payload)

    def poll_chat(self, session_id):
        resp = self._request("get_chat", {"game_id": session_id})
        if resp.get("status") == "ok":
            return resp.get("data") or []
        return []

    # --- Session -----------------------------------------------------------

    def leave_session(self, session_id):
        pass

    def close(self):
        self.disconnect()