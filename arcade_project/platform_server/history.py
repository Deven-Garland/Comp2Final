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
from datastructures.sorting import insertion_sort
import time


class Match:
    def __init__(self, game_id, players, winner, score=0, duration=0, ended_at=None):
        self.game_id = game_id
        self.players = players
        self.winner = winner
        self.score = score
        self.duration = duration
        self.ended_at = time.time() if ended_at is None else float(ended_at)

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

    def add_match(self, game_id, players, winner, score=0, duration=0, ended_at=None):
        match = Match(game_id, players, winner, score=score, duration=duration, ended_at=ended_at)

        for player in players:
            if player not in self.history:
                self.history[player] = ArrayList()

            self.history[player].append(match)

    def get_player_history(self, username, sort_by="date", descending=True):
        if username not in self.history:
            return ArrayList()
        matches = self.history[username]
        if len(matches) <= 1:
            return matches

        if sort_by == "score":
            key_fn = lambda match: (match.score, match.ended_at)
        elif sort_by == "duration":
            key_fn = lambda match: (match.duration, match.ended_at)
        else:
            # Default and fallback: most recent matches first.
            key_fn = lambda match: (match.ended_at, match.game_id)

        sorted_matches = insertion_sort(matches, key=key_fn, reverse=descending)
        result = ArrayList()
        for match in sorted_matches:
            result.append(match)
        return result