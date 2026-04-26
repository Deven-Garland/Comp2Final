"""
hash_table.py - Hash Table implementation

Only required if you implement SparseMatrix using DOK (Option A).

Author: [Your Name]
Date:   [Date]
Lab:    Lab 6 - Sparse World Map
"""


class HashTable:

    def __init__(self, initial_capacity=64):
        self.capacity = initial_capacity
        # TODO
        raise NotImplementedError

    def _hash(self, key):
        # TODO: implement your own hash function — do not use Python's hash()
        raise NotImplementedError

    def set(self, key, value):
        # TODO
        raise NotImplementedError

    def get(self, key, default=None):
        # TODO
        raise NotImplementedError

    def delete(self, key):
        # TODO
        raise NotImplementedError

    def __contains__(self, key):
        # TODO
        raise NotImplementedError

    def __len__(self):
        # TODO
        raise NotImplementedError

    def items(self):
        # TODO
        raise NotImplementedError

    def _resize(self):
        # TODO
        raise NotImplementedError
