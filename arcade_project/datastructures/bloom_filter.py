"""
bloom_filter.py
Bloom filter implementation using k hash functions and a bit array.
Used by AccountManager for O(1) username availability pre-check.
No false negatives; false positives possible (confirmed by hash table lookup).
"""


class BloomFilter:
    """
    Probabilistic set membership structure.
    O(k) insert and lookup where k is the number of hash functions.
    Cannot delete elements.
    """

    def __init__(self, size: int = 100000, num_hashes: int = 5):
        self.size: int = size
        self.num_hashes: int = num_hashes
        self.bit_array: list = [False] * self.size

    def _hash(self, item: str, seed: int) -> int:
        pass

    def add(self, item: str) -> None:
        pass

    def contains(self, item: str) -> bool:
        """
        Returns False if item is definitely NOT in the set.
        Returns True if item is POSSIBLY in the set (may be false positive).
        """
        pass
