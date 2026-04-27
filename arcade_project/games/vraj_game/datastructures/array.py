"""
arraylist.py - Dynamic Array Implementation

Students implement a dynamic array (like Python's list) from scratch.
This will be used throughout the course in place of built-in lists.

Author: [Student Name]
Date: [Date]
Lab: Lab 3 - ArrayList and Inventory System
"""

class ArrayList:
    """
    Implement the methods discussed here: 
    https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
    """

    def __init__(self, initial_capacity=10):
        """
        Initialize a new ArrayList.

        Args:
            initial_capacity (int): Starting capacity of the array.
        """
        self._capacity = initial_capacity
        self._size = 0
        self._data = [None] * self._capacity

    def __len__(self):
        """
        Return number of elements in the ArrayList.
        """
        return self._size

    def get_capacity(self):
        """
        Return current internal capacity of the ArrayList.
        """
        return self._capacity


    def __getitem__(self, index):
        """
        Return element at specified index.

        Raises:
            IndexError: If index out of bounds.
        """
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        return self._data[index]

    def __setitem__(self, index, value):
        """
        Set element at specified index.

        Raises:
            IndexError: If index out of bounds.
        """
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        self._data[index] = value

    def _resize(self):
        """
        Double the capacity of the array when full.
        """
        new_capacity = self._capacity * 2
        new_data = [None] * new_capacity

        for i in range(self._size):
            new_data[i] = self._data[i]

        self._data = new_data
        self._capacity = new_capacity

    def append(self, value):
        """
        Add element to the end of the ArrayList.
        """
        if self._size == self._capacity:
            self._resize()

        self._data[self._size] = value
        self._size += 1

    def insert(self, index, value):
        """
        Insert element at given index.

        Raises:
            IndexError: If index out of bounds.
        """
        if index < 0 or index > self._size:
            raise IndexError("Index out of range")

        if self._size == self._capacity:
            self._resize()

        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]

        self._data[index] = value
        self._size += 1

    def remove(self, value):
        """
        Remove first occurrence of value.

        Raises:
            ValueError: If value not found.
        """
        for i in range(self._size):
            if self._data[i] == value:
                for j in range(i, self._size - 1):
                    self._data[j] = self._data[j + 1]
                self._data[self._size - 1] = None
                self._size -= 1
                return
        raise ValueError("Value not found")

    def pop(self, index=-1):
        """
        Remove and return element at index.

        Raises:
            IndexError: If index out of bounds.
        """
        if self._size == 0:
            raise IndexError("Pop from empty ArrayList")

        if index == -1:
            index = self._size - 1

        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")

        value = self._data[index]

        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]

        self._data[self._size - 1] = None
        self._size -= 1

        return value

    def clear(self):
        """
        Remove all elements from the ArrayList.
        """
        self._data = [None] * self._capacity
        self._size = 0

    def index(self, value):
        """
        Return index of first occurrence of value.

        Raises:
            ValueError: If value not found.
        """
        for i in range(self._size):
            if self._data[i] == value:
                return i
        raise ValueError("Value not found")

    def count(self, value):
        """
        Return number of occurrences of value.
        """
        count = 0
        for i in range(self._size):
            if self._data[i] == value:
                count += 1
        return count

    def extend(self, iterable):
        """
        Append elements from iterable.
        """
        for item in iterable:
            self.append(item)

    def __contains__(self, value):
        """
        Return True if value exists in ArrayList.
        """
        for i in range(self._size):
            if self._data[i] == value:
                return True
        return False

    def __iter__(self):
        """
        Make ArrayList iterable.
        """
        for i in range(self._size):
            yield self._data[i]

    def __str__(self):
        """
        Return user-friendly string representation.
        """
        elements = [str(self._data[i]) for i in range(self._size)]
        return "[" + ", ".join(elements) + "]"

    def __repr__(self):
        """
        Return developer-friendly representation.
        """
        return f"ArrayList(size={self._size}, capacity={self._capacity}, data={self._data[:self._size]})"
