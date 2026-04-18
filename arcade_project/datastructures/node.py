"""
node.py - Node class for linked list

A single node that holds a key/value pair and a pointer to the next node.
Used as the building block for the LinkedList, which is used for collision
chaining in our hash table.

Author: Ellie Lutz
Date: [4/17/2026]
Lab: Final Project - Hash Table
"""


class Node:
    """
    A single node in a linked list. Stores a key, a value, and a pointer
    to the next node in the chain.
    """

    def __init__(self, key, value):
        # The key used for lookups (username in our case)
        self.key = key
        # The value associated with the key (account data)
        self.value = value
        # Pointer to the next node, None if this is the last one
        self.next = None

    def __str__(self):
        # Show key=value so chains are easy to read when debugging
        return f"{self.key}={self.value}"