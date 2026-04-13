"""
screens.py
All UI screens for the arcade client. Each screen is a subclass of Screen.
ArcadeClient switches between these based on server responses.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.connection import ServerConnection


class Screen:
    """Abstract base class for all arcade UI screens."""

    def __init__(self, connection: ServerConnection):
        self.connection: ServerConnection = connection
        self.surface = None  # pygame.Surface assigned at runtime

    def draw(self) -> None:
        pass

    def handle_event(self, event) -> None:
        pass

    def update(self) -> None:
        pass


class LoginScreen(Screen):
    """Displays login and registration form. First screen shown on launch."""

    def __init__(self, connection: ServerConnection):
        super().__init__(connection)
        self.username_input: str = ""
        self.password_input: str = ""
        self.error_message: str = ""

    def draw(self) -> None:
        pass

    def handle_event(self, event) -> None:
        pass

    def submit_login(self) -> bool:
        pass

    def submit_register(self) -> bool:
        pass


class GameBrowser(Screen):
    """Shows the list of available games. Player selects one to join."""

    def __init__(self, connection: ServerConnection):
        super().__init__(connection)
        self.game_list: list = []
        self.selected_game_id: int = None

    def draw(self) -> None:
        pass

    def handle_event(self, event) -> None:
        pass

    def list_games(self) -> list:
        pass

    def join_game(self, game_id: int) -> bool:
        pass


class GameWindow(Screen):
    """Active game screen. Renders game state frames received from C++ server."""

    def __init__(self, connection: ServerConnection, game_server_connection):
        super().__init__(connection)
        self.game_server_connection = game_server_connection
        self.game_state: dict = {}
        self.session_id: int = None
        self.chat_panel: ChatPanel = ChatPanel(connection)

    def draw(self) -> None:
        pass

    def handle_event(self, event) -> None:
        pass

    def render_frame(self, game_state: dict) -> None:
        pass

    def send_input(self, event) -> None:
        pass

    def end_session(self) -> None:
        pass


class ChatPanel(Screen):
    """Overlay chat panel shown during an active game session."""

    def __init__(self, connection: ServerConnection):
        super().__init__(connection)
        self.messages: list = []
        self.input_buffer: str = ""
        self.visible: bool = False

    def draw(self) -> None:
        pass

    def handle_event(self, event) -> None:
        pass

    def send_message(self, text: str) -> None:
        pass

    def receive_message(self, message: dict) -> None:
        pass

    def toggle_visibility(self) -> None:
        pass


class LeaderboardPanel(Screen):
    """Displays global and per-game leaderboards fetched from the platform server."""

    def __init__(self, connection: ServerConnection):
        super().__init__(connection)
        self.scores: list = []
        self.game_filter: int = None

    def draw(self) -> None:
        pass

    def handle_event(self, event) -> None:
        pass

    def fetch_leaderboard(self, game_id: int = None) -> list:
        pass

    def refresh(self) -> None:
        pass
