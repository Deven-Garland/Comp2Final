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
import hashlib
import hmac
import secrets

from datastructures.hash_table import HashTable
from datastructures.bloom_filter import BloomFilter

ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), "accounts_data.json")
HASH_PREFIX = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 120000


def _to_builtin_json(value):
    if isinstance(value, HashTable):
        converted = {}
        for key in value:
            converted[key] = _to_builtin_json(value[key])
        return converted
    if isinstance(value, tuple):
        converted = []
        for item in value:
            converted.append(_to_builtin_json(item))
        return converted
    if isinstance(value, list):
        converted = []
        for item in value:
            converted.append(_to_builtin_json(item))
        return converted
    return value


class Account:
    def __init__(self, username, password, favorite_game="", minutes_played=0, messages_sent=0, avatar=1):
        self._username = username
        self.password = password
        self.favorite_game = favorite_game
        self.minutes_played = minutes_played
        self.messages_sent = messages_sent
        self.avatar = avatar

    @property
    def username(self):
        return self._username

    def __str__(self):
        return f"Account({self.username})"

    def __repr__(self):
        return self.__str__()


class Accounts:
    def __init__(self):
        self.accounts = HashTable()
        self.username_filter = BloomFilter()
        self._load()
        self._migrate_plaintext_passwords()

    def _is_hashed(self, value):
        return isinstance(value, str) and value.startswith(f"{HASH_PREFIX}$")

    def _hash_password(self, password, salt=None):
        if salt is None:
            salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            PBKDF2_ITERATIONS,
        ).hex()
        return f"{HASH_PREFIX}${PBKDF2_ITERATIONS}${salt}${digest}"

    def _verify_password(self, stored_password, provided_password):
        if not self._is_hashed(stored_password):
            # Backward compatibility for legacy plaintext entries.
            return stored_password == provided_password
        try:
            _, iterations, salt, expected = stored_password.split("$", 3)
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                provided_password.encode("utf-8"),
                bytes.fromhex(salt),
                int(iterations),
            ).hex()
            return hmac.compare_digest(digest, expected)
        except Exception:
            return False

    def _migrate_plaintext_passwords(self):
        updated = False
        for username in self.accounts:
            account = self.accounts[username]
            if not self._is_hashed(account.password):
                account.password = self._hash_password(account.password)
                updated = True
        if updated:
            self._save()

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
                    avatar = 1
                else:
                    password = info.get("password", "")
                    favorite_game = info.get("favorite_game", "")
                    minutes_played = info.get("minutes_played", 0)
                    messages_sent = info.get("messages_sent", 0)
                    avatar = info.get("avatar", 1)
                account = Account(username, password, favorite_game, minutes_played, messages_sent, avatar)
                self.accounts[username] = account
                self.username_filter.add(username)
        except Exception as e:
            print(f"[accounts] Could not load accounts file: {e}")

    def _save(self):
        try:
            data = HashTable()
            for key in self.accounts:
                account = self.accounts[key]
                account_data = HashTable()
                account_data["password"] = account.password
                account_data["favorite_game"] = account.favorite_game
                account_data["minutes_played"] = account.minutes_played
                account_data["messages_sent"] = account.messages_sent
                account_data["avatar"] = account.avatar
                data[account.username] = account_data
            with open(ACCOUNTS_FILE, "w") as f:
                json.dump(_to_builtin_json(data), f, indent=2)
        except Exception as e:
            print(f"[accounts] Could not save accounts file: {e}")

    def register(self, username, password):
        if self.username_filter.contains(username):
            if username in self.accounts:
                return False
        account = Account(username, self._hash_password(password))
        self.accounts[username] = account
        self.username_filter.add(username)
        self._save()
        return True

    def login(self, username, password):
        if username not in self.accounts:
            return False
        account = self.accounts[username]
        ok = self._verify_password(account.password, password)
        if ok and not self._is_hashed(account.password):
            # On successful login of a legacy account, upgrade to hashed format.
            account.password = self._hash_password(password)
            self._save()
        return ok

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

    def set_avatar(self, username, avatar_num):
        if username not in self.accounts:
            return False
        self.accounts[username].avatar = int(avatar_num)
        self._save()
        return True

    def get_avatar(self, username):
        if username not in self.accounts:
            return 1
        return getattr(self.accounts[username], 'avatar', 1)

    def __len__(self):
        return len(self.accounts)