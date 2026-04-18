# Catalog (you implement).
"""
chat.py - Per-game-session chat system

Handles chat messages for each game session on the platform. Each active
game session has its own chat history stored in a circular buffer, so
players only see messages from the game they are currently in.

We use a HashTable to map game_id -> CircularBuffer, so looking up a
specific game's chat is O(1). Each buffer only stores the most recent
messages (default 20), older messages get dropped automatically once
the buffer fills up.

Author: Mennah Khaled Dewidar
Date: [4/18/2026]
Lab: Final Project - Catalog
"""
from datastructures.hash_table import HashTable


class Catalog:
    def __init__(self):
        self.players = HashTable()

    def add_player(self, username, data):
        self.players[username] = data

    def get_player(self, username):
        if username not in self.players:
            return None
        return self.players[username]

    def exists(self, username):
        return username in self.players