# Accounts (you implement).
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
Lab: Final Project - Accounts
"""
from datastructures.hash_table import HashTable


class Account:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __str__(self):
        return f"Account({self.username})"

    def __repr__(self):
        """
        returns a developer-friendly string representation (often the same as __str__ for simple classes), used in the interactive shell
        """
        return self.__str__()


class Accounts:
    def __init__(self):
        self.accounts = HashTable()

    def register(self, username, password):
        if username in self.accounts:
            return False

        account = Account(username, password)
        self.accounts[username] = account
        return True

    def login(self, username, password):
        if username not in self.accounts:
            return False

        account = self.accounts[username]
        return account.password == password

    def get_account(self, username):
        if username not in self.accounts:
            return None
        return self.accounts[username]

    def exists(self, username):
        return username in self.accounts

    def remove(self, username):
        if username not in self.accounts:
            return False

        self.accounts.remove(username)
        return True

    def __len__(self):
        return len(self.accounts)