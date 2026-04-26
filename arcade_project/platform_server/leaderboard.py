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
    def __init__(self, metric_weights=None):
        self.tree = BinarySearchTree()
        # HashTable: username -> LeaderboardEntry
        # Lets us update a player's score in O(1) without scanning the BST
        self._entries = HashTable()
        # HashTable: username -> {metric_name: value}
        self._metrics = HashTable()
        # Dict of metric_name -> weight used for score calculation.
        # Example: {"wins": 100, "time_played_seconds": 0.1, "chats_sent": 2}
        self._metric_weights = {}
        if metric_weights is not None:
            self.set_metric_weights(metric_weights)
 
    def add_score(self, username, score):
        # If player already has a score, remove the old entry from the BST
        if username in self._entries:
            self.tree.delete(self._entries[username])
        entry = LeaderboardEntry(username, score)
        self.tree.insert(entry)
        self._entries[username] = entry

    def set_metric_weights(self, metric_weights):
        """
        Configure how each metric contributes to the final score.
        metric_weights should be a dict-like object: {metric_name: weight}
        """
        self._metric_weights = {}
        for metric_name, weight in metric_weights.items():
            self._metric_weights[metric_name] = float(weight)

    def record_metric(self, username, metric_name, amount=1, recompute_score=True):
        """
        Increment one metric for a player.
        This is the main method games should call when events happen.
        """
        if username not in self._metrics:
            self._metrics[username] = {}
        metrics = self._metrics[username]
        current = metrics.get(metric_name, 0)
        metrics[metric_name] = current + amount
        if recompute_score:
            self.recalculate_score(username)

    def set_metric(self, username, metric_name, value, recompute_score=True):
        """
        Set a metric to an exact value (instead of incrementing).
        Useful for values like total_time_seconds pulled from game state.
        """
        if username not in self._metrics:
            self._metrics[username] = {}
        metrics = self._metrics[username]
        metrics[metric_name] = value
        if recompute_score:
            self.recalculate_score(username)

    def get_player_metrics(self, username):
        """
        Return a copy of a player's metrics dictionary.
        """
        if username not in self._metrics:
            return {}
        metrics = self._metrics[username]
        return dict(metrics)

    def calculate_score_from_metrics(self, username):
        """
        Compute weighted score using configured metric weights.
        Metrics with no configured weight default to weight 0.
        """
        if username not in self._metrics:
            return 0
        metrics = self._metrics[username]
        total = 0
        for metric_name, value in metrics.items():
            weight = self._metric_weights.get(metric_name, 0)
            total += value * weight
        return total

    def recalculate_score(self, username):
        """
        Recompute a player's score from tracked metrics and update leaderboard.
        """
        score = self.calculate_score_from_metrics(username)
        self.add_score(username, score)
 
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