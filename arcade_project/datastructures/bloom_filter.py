"""
bloom_filter.py - Bloom Filter Implementation

Checks if a username is possibly taken before hitting the hash table.
False positives are possible but false negatives are not.

Author: [Deven Garland]
Date:   [4/17/2026]
Lab:    Final Project - Bloom Filter
"""

from datastructures.array import ArrayList
from datastructures.hash_table import HashTable

class BloomFilter:

    def __init__(self, bit_array_size=256, num_hashes=3):
        self.bit_array_size = bit_array_size
        self.num_hashes = num_hashes
        self.num_items = 0

        # Fill bit array with zeros
        self.bit_array = ArrayList(initial_capacity=bit_array_size)
        for _ in range(bit_array_size):
            self.bit_array.append(0)

        # Used only for its _hash method
        self._hasher = HashTable(initial_capacity=bit_array_size)

    def _get_position(self, item, seed):
        # Different seed = different position
        return self._hasher._hash(str(item) + str(seed))

    def _get_positions(self, item):
        # Get all k positions for this item
        positions = ArrayList(initial_capacity=self.num_hashes)
        for seed in range(self.num_hashes):
            positions.append(self._get_position(item, seed))
        return positions

    def add(self, item):
        # Set all k bits to 1
        for pos in self._get_positions(item):
            self.bit_array[pos] = 1
        self.num_items += 1

    def contains(self, item):
        # If any bit is 0, item is definitely not in the set
        for pos in self._get_positions(item):
            if self.bit_array[pos] == 0:
                return False
        return True

    def clear(self):
        # Reset all bits to 0
        for i in range(self.bit_array_size):
            self.bit_array[i] = 0
        self.num_items = 0

    def __len__(self):
        return self.num_items

    def __contains__(self, item):
        return self.contains(item)

    def bit_count(self):
        # Count bits set to 1
        total = 0
        for bit in self.bit_array:
            if bit == 1:
                total += 1
        return total

    def false_positive_rate(self):
        # (bits set / total bits) ^ num_hashes
        ratio = self.bit_count() / self.bit_array_size
        result = 1.0
        for _ in range(self.num_hashes):
            result *= ratio
        return result

    def __str__(self):
        return (
            f"BloomFilter(size={self.bit_array_size}, "
            f"hashes={self.num_hashes}, "
            f"items_added={self.num_items}, "
            f"bits_set={self.bit_count()}/{self.bit_array_size}, "
            f"est_fp_rate={self.false_positive_rate():.4f})"
        )

    def __repr__(self):
        return self.__str__()