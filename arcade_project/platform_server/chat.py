"""
chat.py
In-platform chat manager. Broadcasts messages to all players
in the same game session.
"""


class ChatMessage:
    """A single chat message."""

    def __init__(self, sender: str, text: str, game_id: int):
        self.sender: str = sender
        self.text: str = text
        self.game_id: int = game_id
        self.timestamp: float = 0.0


class ChatManager:
    """Routes chat messages to players within the same game session."""

    def __init__(self):
        self.sessions: dict = {}      # game_id -> list of subscriber sockets
        self.history: dict = {}       # game_id -> list of ChatMessage

    def subscribe(self, game_id: int, client_socket) -> None:
        pass

    def unsubscribe(self, game_id: int, client_socket) -> None:
        pass

    def send_message(self, message: ChatMessage) -> None:
        pass

    def get_history(self, game_id: int, limit: int = 50) -> list:
        pass
