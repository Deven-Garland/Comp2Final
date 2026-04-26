# Leaderboards (you implement).
"""
leaderboard.py - Shared leaderboard system

Stores per-player scores for a leaderboard using:
- a BST for sorted score ordering
- a HashTable for O(1) lookup by username

Author: Mennah Khaled Dewidar & Deven Garland
Date: [4/18/2026] Updated: [4/26/2026]
Lab: Final Project - Leaderboard
"""
from datastructures.bst import BinarySearchTree
from datastructures.hash_table import HashTable
from datastructures.sorting import merge_sort
 
 
class LeaderboardEntry:
    def __init__(self, username, score):
        self.username = username
        self.score = score
    def __lt__(self, other):
        if self.score != other.score:
            return self.score < other.score
        return self.username < other.username
    def __gt__(self, other):
        if self.score != other.score:
            return self.score > other.score
        return self.username > other.username
    def __eq__(self, other):
        return self.score == other.score and self.username == other.username
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
        # HashTable: username -> LeaderboardEntry
        # Lets us update a player's score in O(1) without scanning the BST
        self._entries = HashTable()
 
    def add_score(self, username, score):
        # If player already has a score, remove the old entry from the BST
        if username in self._entries:
            self.tree.delete(self._entries[username])
        entry = LeaderboardEntry(username, score)
        self.tree.insert(entry)
        self._entries[username] = entry

    def get_score(self, username):
        """
        Return the current score for a user (or None if missing).
        """
        if username not in self._entries:
            return None
        return self._entries[username].score

    def rank_of(self, username):
        """
        Return 1-based rank (highest score is rank 1), or None if missing.
        """
        if username not in self._entries:
            return None
        sorted_values = merge_sort(
            self._get_sorted(),
            key=lambda entry: (entry.score, entry.username),
            reverse=True,
        )
        rank = 1
        i = 0
        while i < len(sorted_values):
            if sorted_values[i].username == username:
                return rank
            rank += 1
            i += 1
        return None
 
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
        return merge_sort(values, key=lambda entry: (entry.score, entry.username))
 
    def top_k(self, k):
        sorted_values = merge_sort(
            self._get_sorted(),
            key=lambda entry: (entry.score, entry.username),
            reverse=True,
        )
        result = []
        i = 0
        count = 0
        while i < len(sorted_values) and count < k:
            result.append(sorted_values[i])
            i += 1
            count += 1
        return result
 
    def range_query(self, low, high):
        sorted_values = self._get_sorted()
        result = []
        for entry in sorted_values:
            if low <= entry.score <= high:
                result.append(entry)
        return result