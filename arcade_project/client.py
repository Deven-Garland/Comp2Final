"""
client.py
Main entry point for the arcade client.
Run this file to launch the Pygame arcade interface.
"""
from client.arcade_client import ArcadeClient


def main():
    client = ArcadeClient()
    client.run()


if __name__ == "__main__":
    main()
