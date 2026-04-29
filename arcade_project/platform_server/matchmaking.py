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
from datastructures.array import ArrayList
 
 
class QueueEntry:
    def __init__(self, username, game_id="global"):
        self.username = username
        self.game_id = game_id
        self.time = time.time()
 
    def __lt__(self, other):
        return self.time < other.time
 
    def __gt__(self, other):
        return self.time > other.time
 
 
class Matchmaking:
    def __init__(self):
        self.heap = MinHeap()
        self.match_history = ArrayList()
 
    def join_queue(self, username, game_id="global"):
        self.heap.insert(QueueEntry(username, game_id))
 
    def match_players(self, count=2, game_id=None):
        if self.heap.get_size() < count:
            return ArrayList()
 
        if game_id is None:
            game_id = "global"

        result = ArrayList()
        skipped = ArrayList()
 
        while self.heap.get_size() > 0 and len(result) < count:
            entry = self.heap.remove_min()
            if entry.game_id == game_id:
                result.append(entry.username)
            else:
                skipped.append(entry)

        for entry in skipped:
            self.heap.insert(entry)

        if len(result) < count:
            return ArrayList()
 
        self.match_history.append(result)
        return result
 
    def size(self):
        return self.heap.get_size()