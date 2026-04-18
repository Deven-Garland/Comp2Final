"""
chat.py - Per-game-session chat system

Handles chat messages for each game session on the platform. Each active
game session has its own chat history stored in a circular buffer, so
players only see messages from the game they are currently in.

We use a HashTable to map game_id -> CircularBuffer, so looking up a
specific game's chat is O(1). Each buffer only stores the most recent
messages (default 20), older messages get dropped automatically once
the buffer fills up.

Author: Ellie Lutz
Date: [4/17/2026]
Lab: Final Project - Chat
"""
from .accounts import Accounts
from .matchmaking import Matchmaking
from .leaderboard import Leaderboard
from .history import History
from .catalog import Catalog
from .chat import Chat
from .server import PlatformServer