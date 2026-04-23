"""
client.py - Arcade client entry point

Run this to launch the arcade. It starts the platform server in a
background thread automatically, then opens the pygame window.

Authors: Team MOSFET
Date: Spring 2026
Lab: Final Project
"""

import sys
import os
import time
import threading

# Make sure imports from arcade_project/ work
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "arcade_project"))

from arcade_project.platform_server.server import PlatformServer
from arcade_project.client.connection import RequestDispatcher
from arcade_project.client.arcade_client import ArcadeClient

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000


def start_server():
    """Start the platform server + dispatcher in a background thread."""
    srv = PlatformServer()
    dispatcher = RequestDispatcher(srv, host=SERVER_HOST, port=SERVER_PORT)
    print(f"[server] Listening on {SERVER_HOST}:{SERVER_PORT}")
    dispatcher.serve_forever()


def main():
    # Start server in background
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    # Give it a moment to bind the socket before the client connects
    time.sleep(0.3)

    # Launch the client
    client = ArcadeClient()
    client.run()


if __name__ == "__main__":
    main()