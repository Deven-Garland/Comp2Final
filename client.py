"""
client.py - Arcade client entry point

Run this to launch the arcade. Starts the platform server and the
C++ game server in background threads/processes automatically.

Authors: Team MOSFET
Date: Spring 2026
Lab: Final Project
"""

import sys
import os
import time
import threading
import subprocess

# Make sure imports work
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "arcade_project"))

from arcade_project.platform_server.server import run_server
from arcade_project.client.arcade_client import ArcadeClient

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000

# Path to the compiled C++ game server
CPP_SERVER_DIR = os.path.join(os.path.dirname(__file__), "arcade_project", "cpp_server")
CPP_SERVER_BIN = os.path.join(CPP_SERVER_DIR, "server_text")


def start_platform_server():
    """Start the Python platform server in a background thread."""
    try:
        run_server(host=SERVER_HOST, port=SERVER_PORT, players_per_match=1)
    except Exception as e:
        print(f"[platform server] Error: {e}")


def start_cpp_game_server():
    """Start the C++ game server as a subprocess."""
    if not os.path.exists(CPP_SERVER_BIN):
        print(f"[game server] C++ server not found at {CPP_SERVER_BIN}, skipping.")
        return
    try:
        proc = subprocess.Popen(
            [CPP_SERVER_BIN, "--game", "ellie"],
            cwd=CPP_SERVER_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"[game server] C++ server started on port 50072 (pid {proc.pid})")
        proc.wait()
    except Exception as e:
        print(f"[game server] Error starting C++ server: {e}")


def main():
    # Start platform server
    threading.Thread(target=start_platform_server, daemon=True).start()

    # Start C++ game server
    threading.Thread(target=start_cpp_game_server, daemon=True).start()

    # Give servers time to bind
    time.sleep(0.5)

    # Launch the arcade client
    client = ArcadeClient()
    client.run()


if __name__ == "__main__":
    main()