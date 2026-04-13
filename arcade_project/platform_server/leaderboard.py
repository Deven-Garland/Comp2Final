"""
leaderboard.py
Global and per-game leaderboard using a BST for sorted score storage.
"""
from datastructures.bst import BST


class LeaderboardEntry:
    """A single entry in the leaderboard."""

    def __init__(self, username: str, score: int, game_id: int):
        self.username: str = username
        self.score: int = score
        self.game_id: int = game_id


class LeaderboardManager:
    """
    Manages leaderboards for all 5 games plus a global leaderboard.
    Uses a BST per game for O(log n) insert and in-order traversal.
    """

    def __init__(self):
        self.global_bst: BST = BST()
        self.game_bsts: dict = {i: BST() for i in range(1, 6)}

    def submit_score(self, username: str, score: int, game_id: int) -> None:
        pass

    def get_top_n(self, n: int, game_id: int = None) -> list:
        """Returns top n scores. If game_id is None, returns global top n."""
        pass

    def get_player_rank(self, username: str, game_id: int = None) -> int:
        pass

    def get_player_score(self, username: str, game_id: int = None) -> int:
        pass
