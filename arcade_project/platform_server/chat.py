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

import os
import time
from datastructures.hash_table import HashTable
from datastructures.circular_buffer import CircularBuffer
from datastructures.array import ArrayList
 
 
# ---------------------------------------------------------------------------
# Keyword filter — fast, offline, no API needed
# ---------------------------------------------------------------------------
 
_BAD_WORDS = (
    "fuck", "bitch", "hate", "kys", "idiot"
)
 
_GAME_SAFE = (
    "killed", "kill", "die", "died", "death", "shoot", "shot",
    "destroyed", "dead", "murder", "attack", "fight", "destroy"
)
 
 
class KeywordFilter:
    """
    Fast first-pass moderation using two ArrayLists:
      - banned: words that are always blocked
      - safe:   game-context words that are never blocked even if they
                look harmful (prevents false positives like "I killed you")
    O(n) per message. Works offline, no API needed.
    """
    def __init__(self):
        self.banned = ArrayList()
        self.safe = ArrayList()
        for word in _BAD_WORDS:
            self.banned.append(word)
        for word in _GAME_SAFE:
            self.safe.append(word)
 
    def is_clean(self, text):
        words = text.lower().split()
        for word in words:
            if word in self.safe:
                continue
            if word in self.banned:
                return False
        return True
 
 
# ---------------------------------------------------------------------------
# Gemini filter — smart, context-aware, requires API key
# ---------------------------------------------------------------------------
 
class GeminiFilter:
    """
    Uses Google Gemini to moderate messages in context.
    Lazy-initializes the model on first use, same pattern as ai_npc.py.
    Falls back gracefully if the key is missing or the library is not installed.
    """
 
    MODEL = "models/gemini-2.5-flash"
 
    _PROMPT = """
    You are a chat moderator for an arcade game platform.
    Players are competing in classic arcade games and chatting with each other.
    Game-related language like "killed", "destroyed", "die", "shoot" is normal and acceptable.
    Flag ONLY messages that contain:
    - Hate speech or slurs
    - Harassment or threats toward a real person
    - Sexual content
    - Spam or excessive repetition
    - Attempts to bypass the filter such as spaced letters (f u c k), repeated letters (fuckkk), or symbols replacing letters (f*ck)

    Reply with only "CLEAN" or "FLAGGED".
    Message: {message}
    """
 
    def __init__(self):
        self._client = None
        self._model = None  # lazy-initialized on first call
 
    def _ensure_model(self):
        """
        Same pattern as ai_npc.py — tries environment variable first,
        then falls back to .env file. Returns False if setup is incomplete
        so the game keeps running without Gemini.
        """
        if self._client is not None:
            return True
 
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            try:
                from dotenv import load_dotenv
                load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
                api_key = os.environ.get("GEMINI_API_KEY", "")
            except ImportError:
                pass
 
        if not api_key:
            print("[GeminiFilter] GEMINI_API_KEY not set — running keyword filter only.")
            return False
 
        try:
            from google import genai
            self._client = genai.Client(api_key=api_key)
            self._model = self.MODEL
            return True
        except ImportError:
            print("[GeminiFilter] google-generativeai not installed — running keyword filter only.")
            return False
 
    def is_clean(self, text):
        if not self._ensure_model():
            return True  # no Gemini available, let keyword filter decide
        try:
            prompt = self._PROMPT.format(message=text)
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt
            )
            return "CLEAN" in response.text.upper()
        except Exception:
            return True  # if API call fails, don't block the message
 
 
# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------
 
class Message:
    """
    A single chat message. Holds the sender, the text, and the time
    it was sent so the client can display it properly.
    """
    def __init__(self, sender, text):
        self.sender = sender
        self.text = text
        self.timestamp = time.time()
 
    def __str__(self):
        return f"{self.sender}: {self.text}"
 
    def __repr__(self):
        return self.__str__()
 
 
# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
 
class Chat:
    """
    Manages chat for all active game sessions.
    Each game session has its own circular buffer that holds the most
    recent messages.
 
    Moderation runs in two passes:
      1. KeywordFilter — instant, offline, catches obvious bad words
      2. GeminiFilter  — smart, context-aware, catches everything else
    If either flags a message it is blocked before reaching the buffer.
    If Gemini is unavailable the keyword filter still runs on its own.
    """
    def __init__(self, buffer_size=20):
        self.buffer_size = buffer_size
        self.chat_sessions = HashTable()
        self.keyword_filter = KeywordFilter()
        self.gemini_filter = GeminiFilter()
 
    def _is_clean(self, text):
        if not self.keyword_filter.is_clean(text):
            return False
        if not self.gemini_filter.is_clean(text):
            return False
        return True
 
    def start_session(self, game_id):
        if game_id in self.chat_sessions:
            return
        self.chat_sessions[game_id] = CircularBuffer(self.buffer_size)
 
    def end_session(self, game_id):
        if game_id in self.chat_sessions:
            self.chat_sessions.remove(game_id)
 
    def send_message(self, game_id, sender, text):
        """
        Add a new message to a game session's chat.
        Returns True if sent, False if blocked by moderation.
        """
        if not self._is_clean(text):
            return False
        if game_id not in self.chat_sessions:
            self.start_session(game_id)
        message = Message(sender, text)
        buffer = self.chat_sessions[game_id]
        buffer.add(message)
        return True
 
    def get_messages(self, game_id):
        if game_id not in self.chat_sessions:
            return ArrayList()
        buffer = self.chat_sessions[game_id]
        return buffer.get_all()
 
    def get_recent_messages(self, game_id, count):
        all_messages = self.get_messages(game_id)
        if count >= len(all_messages):
            return all_messages
        result = ArrayList()
        start = len(all_messages) - count
        i = start
        while i < len(all_messages):
            result.append(all_messages[i])
            i += 1
        return result
 
    def clear_session(self, game_id):
        if game_id in self.chat_sessions:
            buffer = self.chat_sessions[game_id]
            buffer.clear()
 
    def active_sessions(self):
        result = ArrayList()
        for game_id in self.chat_sessions:
            result.append(game_id)
        return result
 
    def __len__(self):
        return len(self.chat_sessions)