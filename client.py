"""
client.py - Arcade client entry point

Run:  python client.py

How it works:
  - Teammates on their laptops just run:  python3 client.py
    It automatically connects to the platform server on the ECE machine.
  - The person running the ECE server runs:  ./start.sh
    That starts the platform server + all C++ game servers in the background.

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

# ECE server address — teammates' laptops connect here automatically
ECE_HOST = "ece-000.eng.temple.edu"
SERVER_HOST = os.environ.get("ARCADE_PLATFORM_HOST", ECE_HOST)
SERVER_PORT = int(os.environ.get("ARCADE_PLATFORM_PORT", "9000"))

_cpp_children: List[subprocess.Popen] = []


def _client_only() -> bool:
    # if start.sh already started the servers, just run the UI
    return os.environ.get("ARCADE_CLIENT_ONLY", "").strip().lower() in (
        "1", "true", "yes", "on",
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


def _team_game_servers() -> List[tuple]:
    """Host/ports for each teammate C++ server — must match cpp_server default_port_for_game."""
    return [
        ("mennah",   ECE_HOST, 50063),
        ("deven",    ECE_HOST, 50064),
        ("ellie",    ECE_HOST, 50072),
        ("vraj",     ECE_HOST, 50077),
        ("kimberly", ECE_HOST, 50081),
    ]


def start_server() -> None:
    try:
        run_server(
            host="0.0.0.0",        # listen on all interfaces so laptops can reach it
            port=SERVER_PORT,
            players_per_match=1,
            game_servers=_team_game_servers(),
        )
    except Exception as e:
        print(f"[server] Error: {e}")


def main() -> None:
    # ARCADE_CLIENT_ONLY=1 → just open the UI, servers already running via start.sh
    if _client_only():
        print(f"[client] Connecting to platform at {SERVER_HOST}:{SERVER_PORT}")
        ArcadeClient(host=SERVER_HOST, port=SERVER_PORT).run()
        return

    # Running on the ECE server via start.sh — start platform + optional C++ servers
    threading.Thread(target=start_server, daemon=True).start()
    time.sleep(0.35)

    start_cpp_team_servers()
    if _cpp_children:
        time.sleep(0.35)
        atexit.register(stop_cpp_team_servers)

    try:
        ArcadeClient(host=SERVER_HOST, port=SERVER_PORT).run()
    finally:
        stop_cpp_team_servers()


if __name__ == "__main__":
    main()