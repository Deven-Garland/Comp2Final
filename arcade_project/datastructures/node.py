"""
node.py - Node class for Linked List & Binary Search Tree

NODE_LL: A single node that holds a key/value pair and a pointer to the next node.
Used as the building block for the LinkedList, which is used for collision
chaining in our hash table.

NODE_BST: A node which points to the left and right nodes, initially being empty
and holding a given value.

Author: Ellie Lutz & Mennah Khaled Dewidar
Date: [4/17/2026]
Lab: Final Project - Linked List & BST
"""

class Node_LL:
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
    
class Node_BST:
    """
    Implement the methods discussed here:
    https://www.geeksforgeeks.org/python/binary-search-tree-in-python/
    Creating a node class for basic structure
    """
 
    def __init__(self, value):
        """
        instance variables needed: the value stored, left and right node which is initially empty
        """
        self.value = value
        self.left_node = None
        self.right_node = None