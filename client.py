"""
client.py - Arcade client entry point

Run:  python3 client.py

Teammates on their laptops just run: python3 client.py
It automatically connects to the platform server on the ECE machine.
The person running the ECE server runs: python3 start.py

Authors: Team MOSFET
Date: Spring 2026
Lab: Final Project
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "arcade_project"))

from arcade_project.client.arcade_client import ArcadeClient


def main() -> None:
    ArcadeClient().run()


if __name__ == "__main__":
    main()