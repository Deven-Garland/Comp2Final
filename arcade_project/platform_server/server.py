# Platform server (you implement).
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
Lab: Final Project - Server
"""
from platform_server.accounts import Accounts
from platform_server.matchmaking import Matchmaking
from platform_server.leaderboard import Leaderboard
from platform_server.history import History
from platform_server.catalog import Catalog
from platform_server.chat import Chat
from platform_server.data_ingest import DataIngest


class PlatformServer:
    def __init__(self):
        self.accounts = Accounts()
        self.matchmaking = Matchmaking()
        self.leaderboard = Leaderboard()
        self.history = History()
        self.catalog = Catalog()
        self.chat = Chat()

        self.data_ingest = DataIngest(
            self.accounts,
            self.leaderboard,
            self.catalog
        )
        self.data_ingest.load_data()

        self.next_game_id = 1

    def register(self, username, password):
        return self.accounts.register(username, password)

    def login(self, username, password):
        return self.accounts.login(username, password)

    def join_queue(self, username):
        if not self.accounts.exists(username):
            return False

        self.matchmaking.join_queue(username)
        return True

    def try_create_match(self):
        players = self.matchmaking.match_players(1)

        if len(players) == 0:
            return None

        game_id = self.next_game_id
        self.next_game_id += 1

        self.chat.start_session(game_id)

        return game_id, players

    def send_message(self, game_id, username, text):
        self.chat.send_message(game_id, username, text)

    def get_chat(self, game_id):
        return self.chat.get_messages(game_id)

    def end_game(self, game_id, players, winner, score):
        self.history.add_match(game_id, players, winner)

        self.leaderboard.add_score(winner, score)

        self.chat.end_session(game_id)

    def top_players(self, k):
        return self.leaderboard.top_k(k)

    def player_history(self, username):
        return self.history.get_player_history(username)