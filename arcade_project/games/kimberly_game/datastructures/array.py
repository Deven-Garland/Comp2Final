"""
arraylist.py - Dynamic Array Implementation

Students implement a dynamic array (like Python's list) from scratch.
This will be used throughout the course in place of built-in lists.

Author: [Kimberly Olea]
Date: [2/11/26]
Lab: Lab 3 - ArrayList and Inventory System
"""

class ArrayList:
    """
    Implement the methods discussed here: 
    https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
    """
    
    def __init__(self, initial_capacity=10):
        """
        """
        # TODO: Initialize instance variables
        if initial_capacity <= 0:
            initial_capacity = 1
        self._data = [None] * initial_capacity
        self._size = 0
      
    
    # Returns the number of elements when you call len(my_array)
    def __len__(self):
        """
        """
        # TODO: Return the size
        return self._size
    
    
    # Enables bracket notation for accessing elements: my_array[3]
    def __getitem__(self, index):
        """
        """
        # TODO: Return element at index
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError ("ArrayList index out of range")
        return self._data[index]
        
    # Enables bracket notation for setting elements: my_array[3] = 42
    def __setitem__(self, index, value):
        
        # TODO: Set element at index
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("ArrayList assignment index out of range")
        self._data[index] = value
        
    
    def append(self, value):
        """Appending value to the end"""
     
        if self._size == len(self._data):
            new_data = [None] * max(1, len(self._data) *2)
            for i in range(self._size):
                new_data[i] = self._data[i]
            self._data = new_data
        self._data[self._size] = value
        self._size += 1
        
    
    def insert(self, index, value):
    
        """ inserting value before index"""
        if index > self._size:
            index = self._size
        if index < -self._size:
            index = 0
        if index< 0:
            index += self._size

        if self._size == len(self._data):
            new_data = [None]* max(1, len(self._data)*2)
            for i in range(self._size):
                new_data[i] = self._data[i]
            self._data = new_data
        
        for i in range(self._size, index, -1):
            self._data[i] = self._data [i-1]

        self._data[index] = value
        self._size += 1
        
    def remove(self, value):
        """ removing first occurence of value"""
        idx = -1
        for i in range (self._size):
            if self._data[i] == value:
                idx = i
                break
        if idx == -1:
            raise ValueError(f"{value} is not in ArrayList")
      
        for i in range (idx, self._size - 1):
            self._data[i] = self._data[i+1]

        self._data[self._size - 1] = None
        self._size -= 1
    
    
    def pop(self, index=-1):
        """removing and returning item at index """
   
        if self._size == 0:
            raise IndexError("pop from empty ArrayList")
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("pop index out of range")
        value = self._data[index]
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i+1]
        self._data[self._size - 1] = None
        self._size -= 1
        return value
    
    def clear(self):
        """remove all items"""
        
        for i in range(self._size):
            self._data[i] = None
        self._size = 0
        
    
    def index(self, value):
        """ returning firt index of value """
        for i in range(self._size):
            if self._data[i] == value:
                return i
        raise ValueError(f"{value} is not in ArrayList")
            
 

    def count(self, value):
        """ returning number of occurences of value"""
        c = 0
        for i in range(self._size):
            if self._data[i] == value:
                c += 1
        return c
      

    def extend(self, iterable):
        """extend the list by appending elements from the iterable"""
        for x in iterable:
            self.append(x)
     
    
    # Makes the "in" operator work: if 5 in my_array:
    def __contains__(self, value):
        """returning true if value is present """
        for i in range(self._size):
            if self._data[i] == value:
                return True
        return False
      
    
    # Returns a user-friendly string representation when you call str(my_array) or print(my_array)
    def __str__(self):
    
        parts = []
        for i in range(self._size):
            parts.append(repr(self._data[i]))
        return "[" + ", ".join(parts) + "]"
       
    
    # Returns a developer-friendly string representation (often the same as __str__ for simple classes), 
    # used in the interactive shell
    def __repr__(self):
        """
        """
        return str(self)
    
    # Makes the list iterable so you can use it in for loops: for item in my_array:
    def __iter__(self):
        for i in range(self._size):
            yield self._data[i]
        
