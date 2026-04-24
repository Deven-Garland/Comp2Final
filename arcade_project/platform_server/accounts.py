"""
accounts.py - storing everyone's accounts

Handles account storage and set up, also being able to check if usernames 
are already in use or not to prevent data overwritting

Data Structures:
1) Hashtable - to be able to stores usernames/ passwords safely
2) BloomFilter - to be able to check if usernames were used or not

NOTE: removal is tedious as you CANT remove with BloomFilters so there will be a 
hashtable lookup which is unneccassary

Author: Mennah Khaled Dewidar
Date: [4/18/2026]
Lab: Final Project - Algorithm One
"""

import json
import os

from datastructures.hash_table import HashTable
from datastructures.bloom_filter import BloomFilter

ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), "accounts_data.json")


class Account:
    def __init__(self, username, password, favorite_game="", minutes_played=0, messages_sent=0):
        self.username = username
        self.password = password
        self.favorite_game = favorite_game
        self.minutes_played = minutes_played
        self.messages_sent = messages_sent

    def __str__(self):
        return f"Account({self.username})"

    def __repr__(self):
        return self.__str__()


class Accounts:
    def __init__(self):
        self.accounts = HashTable()
        self.username_filter = BloomFilter()
        self._load()

    def _load(self):
        if not os.path.exists(ACCOUNTS_FILE):
            return
        try:
            with open(ACCOUNTS_FILE, "r") as f:
                data = json.load(f)
            for username, info in data.items():
                if isinstance(info, str):
                    password = info
                    favorite_game = ""
                    minutes_played = 0
                    messages_sent = 0
                else:
                    password = info.get("password", "")
                    favorite_game = info.get("favorite_game", "")
                    minutes_played = info.get("minutes_played", 0)
                    messages_sent = info.get("messages_sent", 0)
                account = Account(username, password, favorite_game, minutes_played, messages_sent)
                self.accounts[username] = account
                self.username_filter.add(username)
        except Exception as e:
            print(f"[accounts] Could not load accounts file: {e}")

    def _save(self):
        try:
            data = {}
            for key in self.accounts:
                account = self.accounts[key]
                data[account.username] = {
                    "password": account.password,
                    "favorite_game": account.favorite_game,
                    "minutes_played": account.minutes_played,
                    "messages_sent": account.messages_sent,
                }
            with open(ACCOUNTS_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[accounts] Could not save accounts file: {e}")

    def register(self, username, password):
        if self.username_filter.contains(username):
            if username in self.accounts:
                return False
        account = Account(username, password)
        self.accounts[username] = account
        self.username_filter.add(username)
        self._save()
        return True

    def login(self, username, password):
        if username not in self.accounts:
            return False
        return self.accounts[username].password == password

    def get_account(self, username):
        if username not in self.accounts:
            return None
        return self.accounts[username]

    def exists(self, username):
        return username in self.accounts

    def set_favorite(self, username, game_id):
        if username not in self.accounts:
            return False
        self.accounts[username].favorite_game = game_id
        self._save()
        return True

    def get_favorite(self, username):
        if username not in self.accounts:
            return ""
        return self.accounts[username].favorite_game

    def add_minutes(self, username, minutes):
        if username not in self.accounts:
            return False
        self.accounts[username].minutes_played += minutes
        self._save()
        return True

    def get_minutes(self, username):
        if username not in self.accounts:
            return 0
        return self.accounts[username].minutes_played

    def add_message(self, username):
        """Increment the messages sent count by 1."""
        if username not in self.accounts:
            return False
        self.accounts[username].messages_sent += 1
        self._save()
        return True

    def get_messages_sent(self, username):
        if username not in self.accounts:
            return 0
        return self.accounts[username].messages_sent

    def remove(self, username):
        if username not in self.accounts:
            return False
        self.accounts.remove(username)
        self._save()
        return True

    def __len__(self):
        return len(self.accounts)