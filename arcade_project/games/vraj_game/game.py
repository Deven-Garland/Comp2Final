"""
game.py
Subclasses GameInstance (defined in C++ server interface).
TODO: Fill in game name, genre, and multiplayer details.
"""


class Game:
    """
    Game name: TBD
    Genre: TBD
    Multiplayer: TBD
    Game events: scores, session duration
    """

    def __init__(self, session_id: int, player_id: str):
        self.session_id: int = session_id
        self.player_id: str = player_id
        self.score: int = 0
        self.session_duration: float = 0.0
        self.running: bool = False

    def start(self) -> None:
        pass

    def update(self, delta_time: float) -> None:
        pass

    def render(self, surface) -> None:
        pass

    def handle_event(self, event) -> None:
        pass

    def end(self) -> dict:
        pass
