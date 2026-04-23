"""
connection.py - Client connection to the platform server

Matches the new server protocol: newline-delimited JSON over TCP.
Each request is a JSON object ending with \n, each response is a JSON object ending with \n.

Author: Team MOSFET
Date: Spring 2026
Lab: Final Project
"""

import json
import socket
import threading
import time


class ServerConnection:
    """
    Client-side connection to the platform server.
    Uses newline-delimited JSON protocol to match server.py's RequestDispatcher.
    """

    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self._sock = None
        self._file = None
        self._lock = threading.Lock()
        self._username = None

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
        """Send a request and return the response dict."""
        if payload is None:
            payload = {}
        request = {"action": action, **payload}
        with self._lock:
            self._sock.sendall((json.dumps(request) + "\n").encode("utf-8"))
            line = self._file.readline()
        if not line:
            return {"status": "error", "message": "No response from server"}
        resp = json.loads(line.strip())
        # Normalize to {status, data, message} format
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

    # --- Matchmaking -------------------------------------------------------

    def join_queue(self, skill_rating=1000):
        return self._request("join_queue", {"username": self._username})

    def leave_queue(self):
        pass  # no endpoint yet

    def poll_match(self):
        resp = self._request("try_create_match")
        if resp.get("status") == "ok":
            data = resp.get("data")
            if data and data.get("game_id"):
                return {"session_id": data["game_id"]}
        return None

    # --- Chat --------------------------------------------------------------

    def send_chat(self, message, recipient=None):
        payload = {"game_id": self._current_session, "username": self._username, "text": message}
        return self._request("send_message", payload)

    def poll_chat(self, session_id):
        resp = self._request("get_chat", {"game_id": session_id})
        if resp.get("status") == "ok":
            return resp.get("data") or []
        return []

    # --- Session -----------------------------------------------------------

    def leave_session(self, session_id):
        pass  # no endpoint yet

    # --- Internal ----------------------------------------------------------

    @property
    def _current_session(self):
        return getattr(self, "_session_id", None)

    def close(self):
        self.disconnect()