"""
client.py - Arcade client entry point

Run:  python client.py

Full stack (default on one machine):
  - Python platform server (background thread) on SERVER_HOST:SERVER_PORT
  - Optional C++ game servers when AUTO_START_CPP=1 and server_text exists

Extra players (same ece or laptops) — connect to an already-running platform:
  export ARCADE_CLIENT_ONLY=1
  export ARCADE_PLATFORM_HOST=ece-hostname.cs.school.edu   # or 127.0.0.1 if SSH on ece
  export ARCADE_PLATFORM_PORT=9000
  python client.py

Do NOT run two "full" client.py on the same host: port 9000 can only bind once.
The host that runs the platform should also run C++ games (or set AUTO_START_CPP=1 there).

Authors: Team MOSFET
Date: Spring 2026
Lab: Final Project
"""

from __future__ import annotations

import atexit
import os
import subprocess
import sys
import threading
import time
from typing import List

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "arcade_project"))

from arcade_project.platform_server.server import run_server
from arcade_project.client.arcade_client import ArcadeClient

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000

_cpp_children: List[subprocess.Popen] = []


def _client_only() -> bool:
    return os.environ.get("ARCADE_CLIENT_ONLY", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _cpp_server_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "arcade_project", "cpp_server")


def _find_game_server_binary():
    d = _cpp_server_dir()
    for name in ("server_text", "server_text.exe"):
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return p
    return None


def _auto_start_cpp_enabled() -> bool:
    if _client_only():
        return False
    v = os.environ.get("AUTO_START_CPP", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def start_cpp_team_servers() -> None:
    global _cpp_children
    if not _auto_start_cpp_enabled():
        return

    binary = _find_game_server_binary()
    if not binary:
        print(
            "[client] AUTO_START_CPP=1 but no server_text found. "
            "Build: cd arcade_project/cpp_server && make SERIALIZER=TEXT"
        )
        return

    cpp_dir = _cpp_server_dir()
    games = ("mennah", "deven", "ellie", "vraj", "kimberly")
    kwargs: dict = {"cwd": cpp_dir}
    if sys.platform == "win32":
        cf = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        if cf:
            kwargs["creationflags"] = cf

    for game in games:
        try:
            proc = subprocess.Popen(
                [binary, "--game", game],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **kwargs,
            )
            _cpp_children.append(proc)
            time.sleep(0.12)
        except OSError as e:
            if getattr(e, "errno", None) == 8:
                print(
                    "[client] C++ binary wrong OS (exec format error). "
                    "Build on this machine or use AUTO_START_CPP=0.\n"
                    f"  Binary: {binary}"
                )
                break
            print(f"[client] Could not start C++ server for {game}: {e}")

    if _cpp_children:
        print(f"[client] Started {len(_cpp_children)} C++ game server(s).")


def stop_cpp_team_servers() -> None:
    for p in _cpp_children:
        try:
            p.terminate()
        except Exception:
            pass
    for p in _cpp_children:
        try:
            p.wait(timeout=2.0)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    _cpp_children.clear()


def start_server() -> None:
    try:
        run_server(host=SERVER_HOST, port=SERVER_PORT, players_per_match=1)
    except Exception as e:
        print(f"[server] Error: {e}")


def main() -> None:
    if _client_only():
        gh = os.environ.get("ARCADE_PLATFORM_HOST", "127.0.0.1")
        os.environ.setdefault("PLATFORM_GAME_HOST", gh)
        print(
            "[client] ARCADE_CLIENT_ONLY=1 — UI only; "
            f"connecting to platform at {os.environ.get('ARCADE_PLATFORM_HOST', SERVER_HOST)}:"
            f"{os.environ.get('ARCADE_PLATFORM_PORT', str(SERVER_PORT))}"
        )
        ArcadeClient().run()
        return

    os.environ.setdefault("PLATFORM_GAME_HOST", SERVER_HOST)

    threading.Thread(target=start_server, daemon=True).start()
    time.sleep(0.35)

    start_cpp_team_servers()
    if _cpp_children:
        time.sleep(0.35)
        atexit.register(stop_cpp_team_servers)

    try:
        ArcadeClient().run()
    finally:
        stop_cpp_team_servers()


if __name__ == "__main__":
    main()
