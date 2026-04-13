"""
connection.py
Handles the TCP socket connection from the Pygame client to both servers.
"""
import socket


class ServerConnection:
    """Manages a TCP connection to the Python platform server."""

    def __init__(self, host: str = "localhost", port: int = 5000):
        self.host: str = host
        self.port: int = port
        self.socket: socket.socket = None
        self.connected: bool = False

    def connect(self) -> bool:
        pass

    def disconnect(self) -> None:
        pass

    def send(self, data: dict) -> None:
        pass

    def recv(self) -> dict:
        pass


class GameServerConnection:
    """Manages a TCP connection to the C++ game server."""

    def __init__(self, host: str = "localhost", port: int = 6000):
        self.host: str = host
        self.port: int = port
        self.socket: socket.socket = None
        self.connected: bool = False

    def connect(self) -> bool:
        pass

    def disconnect(self) -> None:
        pass

    def send_input(self, event: dict) -> None:
        pass

    def recv_state(self) -> dict:
        pass
