"""
array.py - Dynamic Array Implementation

Implements a dynamic array similar to Python's built-in list.

Author: Ellie Lutz
Date: 02/09/2026
Lab: Lab 3 - ArrayList and Inventory System
"""

class ArrayList:
    """A dynamic array that mimics basic Python list behavior."""

    def __init__(self, initial_capacity=10):
        """Create an empty ArrayList with a given initial capacity (defaults to 10)"""
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be at least 1")

        self._capacity = initial_capacity
        self._size = 0
        self._data = [None] * self._capacity


    def _resize(self):
        """Double the internal storage capacity."""
        self._capacity *= 2
        new_data = [None] * self._capacity

        for i in range(self._size):
            new_data[i] = self._data[i]

        self._data = new_data


    def __len__(self):
        """Return the number of elements."""
        return self._size


    def __getitem__(self, index):
        """Return the element at the given index (supports negative indexing)."""
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("ArrayList index out of range")
        return self._data[index]


    def __setitem__(self, index, value):
        """Set the element at the given index (supports negative indexing)."""
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("ArrayList index out of range")
        self._data[index] = value


    def append(self, value):
        """Add a value to the end of the list."""
        if self._size == self._capacity:
            self._resize()
        self._data[self._size] = value
        self._size += 1


    def insert(self, index, value):
        """Insert a value at the given index (supports negative indexing)."""
        if index < 0:
            index += self._size

        if index < 0:
            index = 0

        if index > self._size:
            index = self._size

        if self._size == self._capacity:
            self._resize()

        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]

        self._data[index] = value
        self._size += 1


    def remove(self, value):
        """Remove the first occurrence of a value."""
        for i in range(self._size):
            if self._data[i] == value:
                for j in range(i, self._size - 1):
                    self._data[j] = self._data[j + 1]

                self._data[self._size - 1] = None
                self._size -= 1
                return True
        return False


    def pop(self, index=None):
        """Remove and return an element (default is last, supports negative indexing)."""
        if self._size == 0:
            raise IndexError("pop from empty ArrayList")

        if index is None:
            index = self._size - 1
        else:
            if index < 0:
                index += self._size
            if index < 0 or index >= self._size:
                raise IndexError("ArrayList index out of range")

        value = self._data[index]

        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]

        self._data[self._size - 1] = None
        self._size -= 1
        return value


    def clear(self):
        """Remove all elements from the list."""
        self._size = 0


    def index(self, value):
        """Return the index of the first occurrence of a value."""
        for i in range(self._size):
            if self._data[i] == value:
                return i
        raise ValueError("value not found in ArrayList")


    def count(self, value):
        """Return the number of times a value appears."""
        total = 0
        for i in range(self._size):
            if self._data[i] == value:
                total += 1
        return total


    def extend(self, iterable):
        """Append all values from an iterable."""
        for item in iterable:
            self.append(item)


    def __contains__(self, value):
        """Return True if the value exists in the list."""
        for i in range(self._size):
            if self._data[i] == value:
                return True
        return False


    def __str__(self):
        """Return a user-friendly string representation."""
        return "[" + ", ".join(str(self._data[i]) for i in range(self._size)) + "]"


    def __repr__(self):
        """Return a developer-friendly representation."""
        return str(self)


    def __iter__(self):
        """Iterate over elements in the list."""
        for i in range(self._size):
            yield self._data[i]


    def get_capacity(self):
        """Return the internal capacity."""
        return self._capacity


    def get(self, index):
        """Return element at index (supports negative indexing)."""
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Index out of bounds")
        return self._data[index]


    def set(self, index, value):
        """Set element at index (supports negative indexing)."""
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Index out of bounds")
        self._data[index] = value


    def contains(self, value):
        """Return True if value exists."""
        return value in self


    def index_of(self, value):
        """Return index of value or -1 if not found."""
        for i in range(self._size):
            if self._data[i] == value:
                return i
        return -1


    def is_empty(self):
        """Return True if the list is empty."""
        return self._size == 0