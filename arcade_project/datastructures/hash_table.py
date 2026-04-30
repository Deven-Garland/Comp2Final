"""
hash_table.py - Hash table with separate chaining

A hash table that maps keys (like usernames) to values (like account data).
Uses separate chaining for collisions: each bucket is a linked list, and
when two keys hash to the same bucket their entries are added to the chain.

Used by the platform server to store player accounts. Chosen for O(1)
average lookup so login authentication is fast even with 10,000+ players.

Supports:
- O(1) average insert, lookup, and remove
- O(n) worst case if many keys hash to the same bucket
- Automatic resizing (doubles capacity) when load factor gets too high

Author: Ellie Lutz
Date: [4/17/2026]
Lab: Final Project - Hash Table
"""

from .array import ArrayList
from .linked_list import LinkedList


class HashTable:
    """
    A hash table using separate chaining for collision handling.

    Each bucket in the ArrayList holds a LinkedList of (key, value) pairs.
    When the table gets too full we double the capacity and rehash all
    entries into the bigger table.
    """

    def __init__(self, initial_capacity=17):
        """
        Set up an empty hash table with a fixed starting capacity.
        17 is prime which helps spread keys more evenly across buckets.
        """
        # How many buckets the table has
        self.table_capacity = initial_capacity
        # How many key/value pairs are stored in the table
        self.table_size = 0
        # The ArrayList of buckets, each bucket starts as an empty LinkedList
        self.table_buckets = ArrayList(initial_capacity)
        # Fill the array with empty linked lists, one per bucket
        for i in range(initial_capacity):
            self.table_buckets.append(LinkedList())

        # Resize the table once the load factor passes this threshold
        # Load factor = table_size / table_capacity
        # 0.75 is a common choice, lower means fewer collisions but more memory
        self.load_factor = 0.75

    def _hash(self, key):
        """
        Compute the bucket index for a given key.

        Uses FNV-1a, which is a fast hash function that spreads keys evenly
        by XOR-ing each byte into a running hash and multiplying by a prime.
        Handles strings (the main case for usernames) and integers.
        """
        # Convert the key into bytes so we can hash character by character
        if isinstance(key, str):
            data = key.encode("utf-8")
        elif isinstance(key, int):
            # Convert int to 8 bytes so we can hash it the same way as a string
            # The & keeps negative numbers in a valid range
            x = key & 0xFFFFFFFFFFFFFFFF
            data = x.to_bytes(8, "little")
        else:
            # Fall back to string for anything else
            data = str(key).encode("utf-8")

        # FNV-1a constants, these values are the standard 64 bit ones
        hash_value = 0xCBF29CE484222325
        fnv_prime = 0x100000001B3
        mask = 0xFFFFFFFFFFFFFFFF

        # Walk each byte and mix it into the hash
        for byte in data:
            # XOR the byte into the hash then multiply by the prime
            hash_value ^= byte
            hash_value = (hash_value * fnv_prime) & mask

        # Map the big hash value down into a bucket index
        return hash_value % self.table_capacity

    def put(self, key, value):
        """
        Insert a key/value pair. If the key already exists update its value,
        otherwise add a new entry.
        """
        # Find which bucket the key belongs in
        index = self._hash(key)
        bucket = self.table_buckets[index]

        # Check if the key is already in this bucket's chain
        # If it is LinkedList.insert will just update the value in place
        key_was_already_there = bucket.contains(key)

        # Insert handles both new inserts and updates
        bucket.insert(key, value)

        # Only grow the size if this was a new key not an update
        if not key_was_already_there:
            self.table_size += 1

            # Check if the load factor is too high and we need to resize
            if (self.table_size / self.table_capacity) > self.load_factor:
                self._resize()

    def get(self, key, default=None):
        """
        Return the value for a given key.
        Returns `default` (None by default) when the key is not found.
        """
        # Find the bucket and walk its chain looking for the key
        index = self._hash(key)
        bucket = self.table_buckets[index]
        # LinkedList.find returns None if the key is not there
        value = bucket.find(key)
        if value is None and not bucket.contains(key):
            return default
        return value

    def remove(self, key):
        """
        Remove a key from the table. Returns True if removed or False if
        the key was not in the table.
        """
        # Find the bucket and try to remove the key from its chain
        index = self._hash(key)
        bucket = self.table_buckets[index]

        # LinkedList.remove returns True if removed, False if not found
        was_removed = bucket.remove(key)

        # Only shrink the size if something was actually removed
        if was_removed:
            self.table_size -= 1

        return was_removed

    def contains(self, key):
        """
        Return True if the key is in the table False otherwise.
        """
        # Find the bucket and check its chain
        index = self._hash(key)
        bucket = self.table_buckets[index]
        return bucket.contains(key)

    def _resize(self):
        """
        Double the number of buckets and rehash every entry into the new table.

        This is called automatically when the load factor gets too high.
        Resizing is O(n) but happens rarely, so the average cost per insert
        is still O(1).
        """
        # Save the old buckets so we can walk them
        old_buckets = self.table_buckets

        # Double the capacity
        # Using 2x means resizes happen less often as the table grows
        new_capacity = self.table_capacity * 2
        self.table_capacity = new_capacity

        # Build a fresh ArrayList of empty linked lists
        self.table_buckets = ArrayList(new_capacity)
        for i in range(new_capacity):
            self.table_buckets.append(LinkedList())

        # Reset size to 0 because put() below will count them back up
        self.table_size = 0

        # Walk every old bucket and rehash every key into the new table
        # This works because LinkedList iteration yields (key, value) tuples
        for bucket in old_buckets:
            for key, value in bucket:
                # Put handles hashing with the new capacity automatically
                self.put(key, value)

    def __len__(self):
        """
        Return the number of entries when you call len(my_table).
        """
        return self.table_size

    def __getitem__(self, key):
        """
        Enables bracket notation for getting values: my_table[username]
        Raises KeyError if the key is not found.
        """
        # Find the bucket and look up the key
        index = self._hash(key)
        bucket = self.table_buckets[index]

        # We need to check contains first because get returns None for
        # missing keys, but None could also be a valid stored value
        if not bucket.contains(key):
            raise KeyError(f"{key} is not in hash table")

        return bucket.find(key)

    def __setitem__(self, key, value):
        """
        Enables bracket notation for setting values: my_table[username] = data
        """
        # Just call put which already handles insert and update
        self.put(key, value)

    def __delitem__(self, key):
        """
        Enables the del keyword: del my_table[username]
        Raises KeyError if the key is not found.
        """
        # Try to remove, raise KeyError if it wasn't there
        if not self.remove(key):
            raise KeyError(f"{key} is not in hash table")

    def __contains__(self, key):
        """
        Makes the "in" operator work, if username in my_table
        """
        return self.contains(key)

    def clear(self):
        """
        Remove all key/value pairs while keeping current capacity.
        """
        self.table_buckets = ArrayList(self.table_capacity)
        for _ in range(self.table_capacity):
            self.table_buckets.append(LinkedList())
        self.table_size = 0

    def __iter__(self):
        """
        Yield each key in the table one by one, used in for loops.
        """
        # Walk every bucket then every (key, value) pair in each chain
        for bucket in self.table_buckets:
            for key, value in bucket:
                yield key

    def __str__(self):
        """
        Build a user friendly string showing all key value pairs.
        """
        # Start with the opening bracket
        result = "{"

        # Walk every bucket and every pair, adding them to the string
        first = True
        for bucket in self.table_buckets:
            for key, value in bucket:
                # Add a comma and space between pairs
                if not first:
                    result += ", "
                result += f"{key}: {value}"
                first = False

        # Add the closing bracket
        result += "}"

        return result

    def __repr__(self):
        """
        Return the same string representation as __str__.
        """
        return self.__str__()