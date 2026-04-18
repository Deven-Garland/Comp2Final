"""
bloom_filter.py - Bloom Filter Implementation

A Bloom filter is a probabilistic data structure that tests whether an element
is a member of a set. False positives are possible, but false negatives are not.
This means: if the filter says "NO", the element is definitely not in the set.
            if the filter says "YES", the element is PROBABLY in the set.

Uses multiple hash functions to map items to positions in a bit array.
Memory-efficient: stores only bits, not the actual values.

Author: [Deven Garland]
Date:   [4/17/2026]
Lab:    Final Project - Bloom Filter

Implementation notes:
  - Bit array is backed by ArrayList (no built-in list)
  - Hash functions derived from HashTable._hash with different salts
  - No use of Python's built-in dict, set, or list for core storage
"""

from datastructures.array import ArrayList
from datastructures.hash_table import HashTable


class BloomFilter:
    """
    A probabilistic membership-testing data structure.

    Internally maintains a bit array of a fixed size. When an item is added,
    k hash functions each mark one position in the array as 1. To query,
    those same k positions are checked — if any is 0, the item is definitely
    absent; if all are 1, the item is probably present.

    False positive rate decreases as bit_array_size increases and increases
    as more items are added.

   
    """

    def __init__(self, bit_array_size=256, num_hashes=3):
        """
        Initialize the Bloom filter.

        Args:
            bit_array_size (int): Number of bits in the backing array.
                                  Larger = fewer false positives, more memory.
            num_hashes     (int): Number of hash functions to use.
                                  More = fewer false positives, but slower.
        """
        self.bit_array_size = bit_array_size
        self.num_hashes = num_hashes
        # Track how many items have been added
        self.num_items = 0

        # Backing bit array that holds 0 or 1 in each list
        # Using ArrayList instead of a built-in list
        self.bit_array = ArrayList(initial_capacity=bit_array_size)
        for _ in range(bit_array_size):
            self.bit_array.append(0)

        # Single shared HashTable instance used only for its _hash method.
        # We set its capacity to bit_array_size so _hash maps directly into
        # the range [0, bit_array_size) without any extra modulo needed.
        self._hasher = HashTable(initial_capacity=bit_array_size)

    # -------------------------------------------------------------------------
    # Hash functions
    # -------------------------------------------------------------------------

    def _get_position(self, item, seed):
        """
        Compute one bit position for the given item using a salt seed.

        Salting works by appending the seed integer to the item's string
        representation before hashing. This produces a different hash value
        for each seed while still using HashTable._hash under the hood.

        Args:
            item:  The item to hash (any type, converted to string).
            seed:  An integer salt (0, 1, 2, ...) that makes each call unique.

        Returns:
            An integer index in range [0, bit_array_size).
        """
        # Combine item and seed into one string so each seed hashes differently
        salted = str(item) + str(seed)
        # _hash already returns a value in [0, table_capacity)
        # and we set table_capacity = bit_array_size, so no extra modulo needed
        return self._hasher._hash(salted)

    def _get_positions(self, item):
        """
        Return an ArrayList of k bit positions for the given item,
        one per hash function (one per seed value 0..num_hashes-1).

        Args:
            item: Any item (will be converted to string for hashing).

        Returns:
            ArrayList of integer positions.
        """
        positions = ArrayList(initial_capacity=self.num_hashes)
        for seed in range(self.num_hashes):
            positions.append(self._get_position(item, seed))
        return positions

    # -------------------------------------------------------------------------
    # Core operations
    # -------------------------------------------------------------------------

    def add(self, item):
        """
        Add an item to the Bloom filter.

        Sets the bit at each of the item's k hash positions to 1.
        The item itself is NOT stored.

        Args:
            item: The item to add.
        """
        positions = self._get_positions(item)
        for pos in positions:
            self.bit_array[pos] = 1
        self.num_items += 1

    def contains(self, item):
        """
        Test whether an item is possibly in the filter.

        Returns:
            False — item is DEFINITELY not in the set (no false negatives).
            True  — item is PROBABLY in the set (false positives are possible).

        For username checking: if this returns False the username is definitely
        free and you can skip the hash table lookup entirely. If this returns
        True you must still confirm with the hash table since it may be a
        false positive.

        Args:
            item: The item to look up.
        """
        positions = self._get_positions(item)
        for pos in positions:
            if self.bit_array[pos] == 0:
                return False
        return True

    def clear(self):
        """
        Reset the filter, zeroing all bits.
        """
        for i in range(self.bit_array_size):
            self.bit_array[i] = 0
        self.num_items = 0

    # -------------------------------------------------------------------------
    # Informational helpers
    # -------------------------------------------------------------------------

    def __len__(self):
        """
        Return the number of items added.
        """
        return self.num_items

    def __contains__(self, item):
        """
        Allows  'if item in bloom_filter'  syntax.
        """
        return self.contains(item)

    def bit_count(self):
        """
        Return the number of bits currently set to 1.
        Useful for estimating the filter's saturation.
        """
        total = 0
        for bit in self.bit_array:
            if bit == 1:
                total += 1
        return total

    def false_positive_rate(self):
        """
        Estimate the current false positive probability.

        Formula: (bits set / total bits) ^ num_hashes
        As the filter fills up this rate rises toward 1.

        Returns:
            float between 0.0 and 1.0
        """
        ratio = self.bit_count() / self.bit_array_size
        # Raise ratio to the power of num_hashes without using math module
        result = 1.0
        for _ in range(self.num_hashes):
            result *= ratio
        return result

    def __str__(self):
        """
        Return a readable summary of the filter's state.
        """
        bits_set = self.bit_count()
        return (
            f"BloomFilter(size={self.bit_array_size}, "
            f"hashes={self.num_hashes}, "
            f"items_added={self.num_items}, "
            f"bits_set={bits_set}/{self.bit_array_size}, "
            f"est_fp_rate={self.false_positive_rate():.4f})"
        )

    def __repr__(self):
        return self.__str__()