"""
stack.py - Stack data structure implementation

A Last-In-First-Out (LIFO) data structure.
The last item added is the first item removed (like a stack of plates).

Author: [Kimberly Olea]
Date: [2/20/26]
Lab: Lab 4 - Time Travel with Stacks
"""
from datastructures.array import ArrayList

class Stack:
    """
    A LIFO (Last-In-First-Out) data structure.
    
    The last item added is the first item removed.
    Think of it like a stack of plates - you add to the top and remove from the top.
    """
    
    def __init__(self):
        """
        Initialize an empty stack.
        """
        self._items = ArrayList()
    
    def push(self, item):
        """
        Add an item to the top of the stack.
        
        Args:
            item: The item to add to the stack
        """
        self._items.append(item)
    
    def pop(self):
        """
        Remove and return the top item from the stack.
        
        Returns:
            The item that was on top of the stack, or None if empty
        """
        if self.is_empty():
            return None
        return self._items.pop()
    
    def peek(self):
        """
        Return the top item without removing it.
        
        Returns:
            The item on top of the stack, or None if empty
        """
        if self.is_empty():
            return None
        return self._items[len(self._items) - 1]
    
    def is_empty(self):
        """
        Check if the stack is empty.
        
        Returns:
            bool: True if stack is empty, False otherwise
        """
        return len(self._items) == 0
    
    def size(self):
        """
        Get the number of items in the stack.
        
        Returns:
            int: The number of items currently in the stack
        """
        return len(self._items)
    
    def clear(self):
        """Remove all items from the stack."""
        self._items = ArrayList()
    
    def __str__(self):
        """String representation of the stack (for debugging)."""
        return f"Stack(size = {self.size()})"
