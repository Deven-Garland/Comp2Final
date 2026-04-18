# Dataset ingest (you implement).
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
Lab: Final Project - Data_ingest
"""
from datastructures.array import ArrayList


class DataIngest:
    def __init__(self, accounts, leaderboard, catalog):
        self.accounts = accounts
        self.leaderboard = leaderboard
        self.catalog = catalog

    def load_data(self):
        users = ArrayList()

        users.append(("deven", "67", 1500))
        users.append(("ellie", "cute", 1200))
        users.append(("vraj", "yo", 1800))

        for user in users:
            username, password, score = user

            self.accounts.register(username, password)
            self.leaderboard.add_score(username, score)

            self.catalog.add_player(username, {
                "score": score
            })