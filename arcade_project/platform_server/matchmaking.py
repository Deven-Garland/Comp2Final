"""
matchmaking.py
Matchmaking queue using a MinHeap (priority queue) to manage
players waiting to join a game session. Priority = wait time.
"""
from datastructures.heap import MinHeap


class WaitingPlayer:
    """A player waiting to join a game session."""

    def __init__(self, player_id: str, game_id: int, wait_start: float):
        self.player_id: str = player_id
        self.game_id: int = game_id
        self.wait_start: float = wait_start
        self.priority: float = wait_start   # lower = waiting longer = higher priority


class MatchmakingQueue:
    """
    Manages per-game waiting queues using a MinHeap.
    Players who have waited longest are placed into sessions first.
    """

    def __init__(self):
        self.queues: dict = {i: MinHeap() for i in range(1, 6)}  # one heap per game

    def enqueue(self, player: WaitingPlayer) -> None:
        pass

    def dequeue(self, game_id: int) -> WaitingPlayer:
        """Returns the player who has been waiting longest for this game."""
        pass

    def remove_player(self, player_id: str, game_id: int) -> bool:
        """Remove a player who cancelled their request."""
        pass

    def queue_length(self, game_id: int) -> int:
        pass

    def is_empty(self, game_id: int) -> bool:
        pass
