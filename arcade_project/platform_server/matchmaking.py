# Matchmaking (you implement).
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
Lab: Final Project - Matchmaking
"""
import time
from datastructures.heap import MinHeap


class QueueEntry:
    def __init__(self, username):
        self.username = username
        self.time = time.time()

    def __lt__(self, other):
        return self.time < other.time

    def __gt__(self, other):
        return self.time > other.time


class Matchmaking:
    def __init__(self):
        self.heap = MinHeap()

    def join_queue(self, username):
        self.heap.insert(QueueEntry(username))

    def match_players(self, count=2):
        if self.heap.get_size() < count:
            return []

        result = []

        for i in range(count):
            entry = self.heap.remove_min()
            result.append(entry.username)

        return result

    def size(self):
        return self.heap.get_size()