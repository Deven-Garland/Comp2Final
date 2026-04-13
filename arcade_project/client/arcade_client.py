"""
arcade_client.py
Main entry point for the Pygame arcade client.
Manages the game loop and switches between screens.
"""
from client.connection import ServerConnection, GameServerConnection
from client.screens import Screen, LoginScreen, GameBrowser, GameWindow, LeaderboardPanel


class ArcadeClient:
    """
    Central client class. Owns the server connections and manages
    which Screen is currently active.
    """

    def __init__(self):
        self.player_id: str = ""
        self.session_token: str = ""
        self.current_screen: Screen = None
        self.connection: ServerConnection = ServerConnection()
        self.game_connection: GameServerConnection = GameServerConnection()
        self.running: bool = False
        self.clock = None  # pygame.time.Clock assigned at runtime

    def run(self) -> None:
        """Main game loop."""
        pass

    def switch_screen(self, screen: Screen) -> None:
        """Replace the current screen with a new one."""
        pass

    def send(self, data: dict) -> None:
        """Send a message to the platform server."""
        pass

    def handle_server_message(self, message: dict) -> None:
        """Route incoming server messages to the correct screen."""
        pass

    def quit(self) -> None:
        """Clean up connections and exit."""
        pass
