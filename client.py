"""
client.py - Arcade client entry point

Run:  python client.py

This starts, by default:
  - Python platform server (background thread) on SERVER_HOST:SERVER_PORT
  - All five C++ team game servers (subprocesses), if server_text is built under
    arcade_project/cpp_server/

Disable auto C++ with:  set AUTO_START_CPP=0   (Windows)  or  export AUTO_START_CPP=0

On eceserver / production, run platform + C++ separately; laptops only run the client
with SERVER_HOST pointing at the host.

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

# Make sure imports work
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "arcade_project"))

from arcade_project.platform_server.server import run_server
from arcade_project.client.arcade_client import ArcadeClient

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000

# Populated if we auto-start C++ game servers (for cleanup)
_cpp_children: List[subprocess.Popen] = []


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
    v = os.environ.get("AUTO_START_CPP", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def start_cpp_team_servers() -> None:
    """Start one C++ process per team game (--game …) if the binary exists."""
    global _cpp_children
    if not _auto_start_cpp_enabled():
        print("[client] AUTO_START_CPP disabled; start C++ servers manually if needed.")
        return

    binary = _find_game_server_binary()
    if not binary:
        print(
            "[client] No server_text / server_text.exe in arcade_project/cpp_server/. "
            "Build with make (Linux/WSL) or start_team_servers.sh on eceserver."
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
    """Start the platform server in a background thread."""
    try:
        run_server(host=SERVER_HOST, port=SERVER_PORT, players_per_match=1)
    except Exception as e:
        print(f"[server] Error: {e}")


def main() -> None:
    # So platform auto-registers team games for the same host laptops use locally
    os.environ.setdefault("PLATFORM_GAME_HOST", SERVER_HOST)

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(0.35)

    start_cpp_team_servers()
    time.sleep(0.35)

    atexit.register(stop_cpp_team_servers)

    try:
        client = ArcadeClient()
        client.run()
    finally:
        stop_cpp_team_servers()


if __name__ == "__main__":
    main()
