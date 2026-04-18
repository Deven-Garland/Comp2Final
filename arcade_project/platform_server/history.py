# Match history (you implement).
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
Lab: Final Project - History
"""
from datastructures.hash_table import HashTable
from datastructures.array import ArrayList


class Match:
    def __init__(self, game_id, players, winner):
        self.game_id = game_id
        self.players = players
        self.winner = winner

    def __str__(self):
        return f"Game {self.game_id} Winner: {self.winner}"

    def __repr__(self):
        """
        returns a developer-friendly string representation (often the same as __str__ for simple classes), used in the interactive shell
        """
        return self.__str__()


class History:
    def __init__(self):
        self.history = HashTable()

    def add_match(self, game_id, players, winner):
        match = Match(game_id, players, winner)

        for player in players:
            if player not in self.history:
                self.history[player] = ArrayList()

            self.history[player].append(match)

    def get_player_history(self, username):
        if username not in self.history:
            return ArrayList()

        return self.history[username]