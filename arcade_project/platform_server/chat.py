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

import time

from datastructures.hash_table import HashTable
from datastructures.circular_buffer import CircularBuffer


class Message:
    """
    A single chat message. Holds the sender, the text, and the time
    it was sent so the client can display it properly.
    """

    def __init__(self, sender, text):
        # Username of the player who sent the message
        self.sender = sender
        # The actual message text
        self.text = text
        # When the message was sent, as a unix timestamp
        # This lets the client format it however it wants
        self.timestamp = time.time()

    def __str__(self):
        # Display format like: "ellie: hello world"
        return f"{self.sender}: {self.text}"

    def __repr__(self):
        return self.__str__()


class Chat:
    """
    Manages chat for all active game sessions.

    Each game session has its own circular buffer that holds the most
    recent messages. When a new game session starts we create a buffer
    for it, when it ends we delete it.
    """

    def __init__(self, buffer_size=20):
        """
        Set up an empty chat system.

        buffer_size is how many messages each game session keeps in
        history (default 20).
        """
        # Store how big each session's buffer should be so we use the
        # same size every time we create a new session
        self.buffer_size = buffer_size
        # Maps game_id -> CircularBuffer of Message objects
        # HashTable is O(1) lookup so finding a specific game's chat is fast
        self.chat_sessions = HashTable()

    def start_session(self, game_id):
        """
        Create a new empty chat buffer for a game session.
        Call this when a new game starts.
        """
        # Make sure we don't overwrite an existing session by accident
        if game_id in self.chat_sessions:
            return

        # Fresh buffer for this session with the configured size
        self.chat_sessions[game_id] = CircularBuffer(self.buffer_size)

    def end_session(self, game_id):
        """
        Delete a game session's chat history.
        Call this when a game ends to free up the memory.
        """
        # Only remove if it exists so we don't crash on double-ends
        if game_id in self.chat_sessions:
            self.chat_sessions.remove(game_id)

    def send_message(self, game_id, sender, text):
        """
        Add a new message to a game session's chat.

        If the session doesn't exist yet we create it automatically so
        the caller doesn't have to remember to start the session first.
        If the buffer is full the oldest message gets overwritten.
        """
        # Auto-create the session if this is the first message
        if game_id not in self.chat_sessions:
            self.start_session(game_id)

        # Wrap the text in a Message object so we can track sender and time
        message = Message(sender, text)

        # Add to the buffer, circular buffer handles overflow automatically
        buffer = self.chat_sessions[game_id]
        buffer.add(message)

    def get_messages(self, game_id):
        """
        Get all messages for a game session, oldest first.
        Returns an empty list if the session doesn't exist.
        """
        # Return empty list for non-existent sessions so the client
        # doesn't have to handle None or KeyError
        if game_id not in self.chat_sessions:
            return []

        # Buffer's get_all already returns oldest to newest
        buffer = self.chat_sessions[game_id]
        return buffer.get_all()

    def get_recent_messages(self, game_id, count):
        """
        Get the most recent N messages from a game session.
        Useful for showing a preview or for late-joining players.
        """
        # Get everything then slice the last N from it
        all_messages = self.get_messages(game_id)

        # If they asked for more messages than exist just return them all
        if count >= len(all_messages):
            return all_messages

        # Return the last count messages (most recent)
        return all_messages[-count:]

    def clear_session(self, game_id):
        """
        Remove all messages from a session's chat but keep the session.
        Useful if we want to reset chat without ending the game.
        """
        # Only clear if the session exists
        if game_id in self.chat_sessions:
            buffer = self.chat_sessions[game_id]
            buffer.clear()

    def active_sessions(self):
        """
        Return a list of all game_ids that have active chat sessions.
        """
        result = []
        # HashTable iteration yields keys which are the game_ids
        for game_id in self.chat_sessions:
            result.append(game_id)
        return result

    def __len__(self):
        """
        Return the number of active chat sessions.
        """
        return len(self.chat_sessions)