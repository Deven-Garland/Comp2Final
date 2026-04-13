"""
bst.py
Binary Search Tree implementation.
Used by LeaderboardManager for sorted score storage and in-order traversal.
"""


class BSTNode:
    """A single node in the binary search tree."""

    def __init__(self, key: int, value):
        self.key: int = key
        self.value = value
        self.left: BSTNode = None
        self.right: BSTNode = None


class BST:
    """
    Binary Search Tree.
    Supports O(log n) average insert, search, and delete.
    In-order traversal yields sorted scores for leaderboard queries.
    """

    def __init__(self):
        self.root: BSTNode = None
        self.size: int = 0

    def insert(self, key: int, value) -> None:
        pass

    def search(self, key: int) -> BSTNode:
        pass

    def delete(self, key: int) -> bool:
        pass

    def inorder(self) -> list:
        """Returns all (key, value) pairs in ascending order."""
        pass

    def top_n(self, n: int) -> list:
        """Returns the n highest-key entries (reverse in-order traversal)."""
        pass

    def min_node(self) -> BSTNode:
        pass

    def max_node(self) -> BSTNode:
        pass

    def __len__(self) -> int:
        return self.size
