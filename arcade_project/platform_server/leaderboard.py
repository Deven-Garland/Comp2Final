# Leaderboards (you implement).
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
Lab: Final Project - Leaderboard
"""
from datastructures.bst import BinarySearchTree


class LeaderboardEntry:
    def __init__(self, username, score):
        self.username = username
        self.score = score

    def __lt__(self, other):
        return self.score < other.score

    def __gt__(self, other):
        return self.score > other.score

    def __eq__(self, other):
        return self.score == other.score

    def __str__(self):
        return f"{self.username}: {self.score}"

    def __repr__(self):
        """
        returns a developer-friendly string representation (often the same as __str__ for simple classes), used in the interactive shell
        """
        return self.__str__()


class Leaderboard:
    def __init__(self):
        self.tree = BinarySearchTree()

    def add_score(self, username, score):
        entry = LeaderboardEntry(username, score)
        self.tree.insert(entry)

    def _get_sorted(self):
        """
        uses BST inorder traversal format
        """
        result = {0: 0}
        self.tree.inorder(self.tree.root, result)

        values = []
        i = 1
        while i <= result[0]:
            values.append(result[i])
            i += 1

        return values

    def top_k(self, k):
        sorted_values = self._get_sorted()

        result = []
        i = len(sorted_values) - 1

        count = 0
        while i >= 0 and count < k:
            result.append(sorted_values[i])
            i -= 1
            count += 1

        return result

    def range_query(self, low, high):
        sorted_values = self._get_sorted()

        result = []
        for entry in sorted_values:
            if low <= entry.score <= high:
                result.append(entry)

        return result