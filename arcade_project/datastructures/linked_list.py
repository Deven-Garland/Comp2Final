"""
linked_list.py - Simple singly linked list implementation

A basic singly linked list used for collision chaining in the hash table.
When two keys hash to the same bucket, the entries are stored as a chain
of linked nodes rather than overwriting each other.

Supports:
- O(1) insertion at the head
- O(n) search by key through the chain
- O(n) removal by key

Author: [Deven Garland]
Date: [4/17/2026]
Lab: Final Project - Hash Table
"""

from .node import Node


class LinkedList:
    """
    A singly linked list of (key, value) pairs.

    Used as the bucket type in our hash table. Each bucket is a LinkedList,
    and collisions are handled by adding new nodes to the chain.
    """

    def __init__(self):
        """
        Initialize an empty linked list.
        """
        # First node in the chain, None if list is empty
        self.head = None
        # Number of nodes currently in the list
        self.size = 0

    def insert(self, key, value):
        """
        Insert a key/value pair. If key already exists update its value,
        otherwise add a new node at the head of the list.
        """
        # Walk the list to see if the key is already there
        current = self.head
        while current is not None:
            if current.key == key:
                # Key already exists so just update the value
                current.value = value
                return
            current = current.next

        # Key was not found so add a new node at the head
        # We insert at the head because it's O(1) instead of walking to the end
        new_node = Node(key, value)
        new_node.next = self.head
        self.head = new_node
        # Increment size
        self.size += 1

    def find(self, key):
        """
        Find a value by its key. Returns the value if found or None if not.
        """
        # Walk the list looking for a matching key
        current = self.head
        while current is not None:
            if current.key == key:
                return current.value
            current = current.next

        # Key was not found in the chain
        return None

    def contains(self, key):
        """
        Return True if key is in the list, False otherwise.
        """
        # Walk the list looking for a matching key
        current = self.head
        while current is not None:
            if current.key == key:
                return True
            current = current.next

        # Key was not found
        return False

    def remove(self, key):
        """
        Remove the node with the given key. Returns True if removed,
        False if the key wasn't in the list.
        """
        # If list is empty there is nothing to remove
        if self.head is None:
            return False

        # Special case, removing the head node
        if self.head.key == key:
            self.head = self.head.next
            self.size -= 1
            return True

        # Walk the list keeping track of the previous node so we can
        # unlink the target node by skipping over it
        previous = self.head
        current = self.head.next
        while current is not None:
            if current.key == key:
                # Unlink the current node from the chain
                previous.next = current.next
                self.size -= 1
                return True
            previous = current
            current = current.next

        # Key was not found in the chain
        return False

    def is_empty(self):
        """
        Return True if the list has no nodes.
        """
        return self.head is None

    def __len__(self):
        """
        Return the number of nodes when you call len(my_list).
        """
        return self.size

    def __contains__(self, key):
        """
        Makes the "in" operator work, if key in my_list
        """
        return self.contains(key)

    def __iter__(self):
        """
        Yield each (key, value) pair one by one, used in for loops.
        This lets the hash table walk the chain when rehashing during resize.
        """
        current = self.head
        while current is not None:
            # Yield as a tuple so the hash table can unpack key and value
            yield (current.key, current.value)
            current = current.next

    def __str__(self):
        """
        Build a user friendly string, like [key1=val1, key2=val2]
        """
        # Start with the opening bracket
        result = "["

        # Walk the list and convert each node to string
        current = self.head
        first = True
        while current is not None:
            # Add a comma and space between nodes
            if not first:
                result += ", "
            result += str(current)
            first = False
            current = current.next

        # Add the closing bracket
        result += "]"

        return result

    def __repr__(self):
        """
        Return the same string representation as __str__.
        """
        return self.__str__()