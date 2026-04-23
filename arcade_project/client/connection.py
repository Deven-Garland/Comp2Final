# Platform / game sockets (you implement).
"""
connection.py - Per-game-session chat system

Author: Mennah Khaled Dewidar
Date: [4/23/2026]
Lab: Final Project - connection.py
"""
import json
import socket
import struct
import threading
import time

from arcade_project.platform_server.server import PlatformServer

# ---------------------------------------------------------------------------
# Wire protocol: 4-byte length header + JSON body
# ---------------------------------------------------------------------------

def _send(sock, obj):
    body = json.dumps(obj).encode()
    sock.sendall(struct.pack(">I", len(body)) + body)

def _recv(sock):
    length = struct.unpack(">I", _recv_bytes(sock, 4))[0]
    return json.loads(_recv_bytes(sock, length))

def _recv_bytes(sock, n):
    buf = b""
    while len(buf) < n:
        buf += sock.recv(n - len(buf))
    return buf


# ---------------------------------------------------------------------------
# Client helpers
# ---------------------------------------------------------------------------

class ServerConnection:
    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self._sock = None
        self._token = None
        self._username = None

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self.host, self.port))

    def disconnect(self):
        if self._sock:
            self._sock.close()
            self._sock = None

    def _request(self, action, payload):
        frame = {"action": action, "payload": payload}
        if self._token:
            frame["token"] = self._token
        _send(self._sock, frame)
        return _recv(self._sock)

    def login(self, username, password):
        resp = self._request("login", {"username": username, "password": password})
        if resp["status"] == "ok":
            self._username = username
            self._token = resp["data"].get("token")
        return resp

    def register(self, username, password, email):
        return self._request("register", {"username": username,
                                          "password": password,
                                          "email": email})

    def join_queue(self, skill_rating=1000):
        return self._request("join_queue", {"username": self._username,
                                            "skill_rating": skill_rating})

    def send_chat(self, message, recipient=None):
        payload = {"sender": self._username, "message": message}
        if recipient:
            payload["recipient"] = recipient
        return self._request("send_chat", payload)

    def get_leaderboard(self, top_n=10):
        return self._request("get_leaderboard", {"top_n": top_n})


# ---------------------------------------------------------------------------
# Server dispatcher
# ---------------------------------------------------------------------------

class RequestDispatcher:
    def __init__(self, server: PlatformServer, host="127.0.0.1", port=9000):
        self._srv = server
        self.host = host
        self.port = port
        self._sessions = {}   # token -> username
        self._chat_log = []

    def serve_forever(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(16)
        while True:
            client, _ = sock.accept()
            threading.Thread(target=self._handle, args=(client,), daemon=True).start()

    def _handle(self, client):
        try:
            while True:
                req  = _recv(client)
                resp = self._dispatch(req)
                _send(client, resp)
        except Exception:
            client.close()

    def _dispatch(self, req):
        action  = req.get("action")
        payload = req.get("payload", {})

        if action == "login":
            # accounts.login() returns True/False, wrap it in a dict
            ok = self._srv.login(payload["username"], payload["password"])
            if ok:
                tok = f"{payload['username']}:{time.time()}"
                self._sessions[tok] = payload["username"]
                return {"status": "ok", "data": {"token": tok}}
            return {"status": "error", "message": "Invalid username or password."}

        if action == "register":
            # accounts.register() returns True/False, wrap it in a dict
            ok = self._srv.register(payload["username"], payload["password"])
            if ok:
                return {"status": "ok", "data": {}}
            return {"status": "error", "message": "Username already taken."}

        if action == "join_queue":
            # server.join_queue() takes just username
            ok = self._srv.join_queue(payload["username"])
            if ok:
                return {"status": "ok", "data": {}}
            return {"status": "error", "message": "Could not join queue."}

        if action == "queue_status":
            # check if a match is ready
            result = self._srv.try_create_match()
            if result is not None:
                game_id, players = result
                return {"status": "ok", "data": {"session_id": game_id, "players": players}}
            return {"status": "ok", "data": {}}  # still waiting

        if action == "send_chat":
            entry = {"sender":    payload["sender"],
                     "message":   payload["message"],
                     "recipient": payload.get("recipient"),
                     "time":      time.time()}
            self._chat_log = self._chat_log[-499:] + [entry]
            return {"status": "ok", "data": {"delivered": True}}

        if action == "get_chat":
            messages = self._srv.get_chat(payload.get("game_id"))
            return {"status": "ok", "data": {"messages": messages or []}}

        if action == "get_leaderboard":
            top = self._srv.top_players(payload.get("top_n", 10))
            serialized = [{"username": e.username, "score": e.score} for e in (top or [])]
            return {"status": "ok", "data": {"leaderboard": serialized}}

        return {"status": "error", "message": f"Unknown action: {action}"}


# ---------------------------------------------------------------------------
# Smoke checklist: login / browse / queue / chat
# ---------------------------------------------------------------------------

def run_smoke_checks(host="127.0.0.1", port=9000):
    user = f"smoke_{int(time.time())}"
    conn = ServerConnection(host, port)
    conn.connect()

    results = {}

    # 1. REGISTER + LOGIN
    conn.register(user, "pass1234", f"{user}@test.com")
    r = conn.login(user, "pass1234")
    results["login"] = r["status"] == "ok" and conn._token is not None

    # 2. BROWSE leaderboard
    r = conn.get_leaderboard(10)
    results["browse"] = r["status"] == "ok" and "leaderboard" in r["data"]

    # 3. QUEUE
    r = conn.join_queue(skill_rating=1100)
    results["queue"] = r["status"] == "ok"

    # 4. CHAT
    r = conn.send_chat("hello from smoke test")
    results["chat"] = r["status"] == "ok" and r["data"]["delivered"]

    conn.disconnect()

    print("\nSmoke Checklist Results")
    print("-" * 30)
    for check, passed in results.items():
        print(f"  {'PASS' if passed else 'FAIL'}  {check}")
    print(f"\n{sum(results.values())}/{len(results)} passed\n")

    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    PORT = 9002
    srv = PlatformServer()

    dispatcher = RequestDispatcher(srv, port=PORT)
    threading.Thread(target=dispatcher.serve_forever, daemon=True).start()
    time.sleep(0.1)

    results = run_smoke_checks(port=PORT)
    sys.exit(0 if all(results.values()) else 1)