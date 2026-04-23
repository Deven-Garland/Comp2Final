"""
accounts.py - Player account management

Handles player registration and login. Uses a HashTable for fast O(1)
lookups since login is one of the most frequent operations.

Accounts are saved to a JSON file so they persist between server restarts.

Author: Mennah Khaled Dewidar
Date: [4/18/2026]
Lab: Final Project - Accounts
"""

import json
import os

from datastructures.hash_table import HashTable


# Where accounts are saved on disk
ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), "accounts_data.json")


class Account:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __str__(self):
        return f"Account({self.username})"

    def __repr__(self):
        return self.__str__()


class Accounts:
    def __init__(self):
        self.accounts = HashTable()
        self._load()

    def _load(self):
        """Load accounts from disk if the file exists."""
        if not os.path.exists(ACCOUNTS_FILE):
            return
        try:
            with open(ACCOUNTS_FILE, "r") as f:
                data = json.load(f)
            for username, password in data.items():
                self.accounts[username] = Account(username, password)
        except Exception as e:
            print(f"[accounts] Could not load accounts file: {e}")

    def _save(self):
        """Save all accounts to disk as a JSON file."""
        try:
            data = {}
            for key in self.accounts:
                account = self.accounts[key]
                data[account.username] = account.password
            with open(ACCOUNTS_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[accounts] Could not save accounts file: {e}")

    def register(self, username, password):
        if username in self.accounts:
            return False
        account = Account(username, password)
        self.accounts[username] = account
        self._save()
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
        self._save()
        return True

    def __len__(self):
        return len(self.accounts)