"""
client.py - Arcade client entry point

Run this to launch the arcade. Starts the platform server in a
background thread automatically, then opens the pygame window.

Authors: Team MOSFET
Date: Spring 2026
Lab: Final Project
"""

import sys
import os
import time
import threading

# Make sure imports work
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "arcade_project"))

from arcade_project.platform_server.server import run_server
from arcade_project.client.arcade_client import ArcadeClient

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000


def start_server():
    """Start the platform server in a background thread."""
    try:
        run_server(host=SERVER_HOST, port=SERVER_PORT, players_per_match=1)
    except Exception as e:
        print(f"[server] Error: {e}")


def main():
    # Start server in background
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    # Give it a moment to bind
    time.sleep(0.5)

    # Launch the client
    client = ArcadeClient()
    client.run()


if __name__ == "__main__":
    main()