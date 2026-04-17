"""
stack.py - Stack data structure implementation

A Last-In-First-Out (LIFO) data structure.
The last item added is the first item removed (like a stack of plates).

Author: [Deven Garland]
Date: [2/16/2026]
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
        # Create empty stack
        self._data=ArrayList()

    
    def push(self, item):

        """
        Add an item to the top of the stack.
        
        Args:
            item: The item to add to the stack
        """
        # Adds value to the top of the stack
        self._data.append(item)
       
    
    def pop(self):
        """
        Remove and return the top item from the stack.
        
        Returns:
            The item that was on top of the stack, or None if empty
        """
        # Checks for stack then uses pop method
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        return self._data.pop()
    
    def peek(self):
        """
        Return the top item without removing it.
        
        Returns:
            The item on top of the stack, or None if empty
        """
        # Checks if empty then returns top/last value
        if self.is_empty():
            raise IndexError("Peek from empty stack")
        return self._data[-1]
    
    def is_empty(self):
        """
        Check if the stack is empty.
        
        Returns:
            bool: True if stack is empty, False otherwise
        """
        # Checks if len is 0 
        return len(self._data) == 0
    
    def size(self):
        """
        Get the number of items in the stack.
        
        Returns:
            int: The number of items currently in the stack
        """
        # Returns the len of the stack
        return len(self._data)

        
    
    def clear(self):
        """Remove all items from the stack."""
        return self._data.clear()
    
    def __str__(self):
        """String representation of the stack (for debugging)."""
        return str(self._data)
