"""
game.py — Ellie's game: Eli's Legacy (Fantasy/Adventure)
Subclasses GameInstance (defined in C++ server interface).
This Python module handles client-side rendering for Ellie's game.
"""


class ElliesLegacyGame:
    """
    Eli's Legacy — Fantasy/Adventure game.
    Players compete independently for the highest score on a shared leaderboard.
    Chat with other players playing simultaneously.
    Game events: session duration, score milestones.
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
        """Returns session summary dict with score and duration."""
        pass
