"""
heap.py
Min-heap (priority queue) implementation using an array.
Used by MatchmakingQueue to serve the longest-waiting player first.
"""


class MinHeap:
    """
    Array-based min-heap.
    O(log n) insert (sift-up), O(log n) extract-min (sift-down), O(1) peek.
    """

    def __init__(self):
        self.data: list = []

    def insert(self, priority: float, value) -> None:
        pass

    def extract_min(self):
        """Removes and returns the element with the smallest priority."""
        pass

    def peek(self):
        """Returns the min element without removing it."""
        pass

    def _sift_up(self, index: int) -> None:
        pass

    def _sift_down(self, index: int) -> None:
        pass

    def _parent(self, index: int) -> int:
        return (index - 1) // 2

    def _left(self, index: int) -> int:
        return 2 * index + 1

    def _right(self, index: int) -> int:
        return 2 * index + 2

    def __len__(self) -> int:
        return len(self.data)

    def is_empty(self) -> bool:
        return len(self.data) == 0
