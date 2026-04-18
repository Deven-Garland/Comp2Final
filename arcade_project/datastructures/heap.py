"""
heap.py - Dynamic Array Implementation

I implemented a dynamic binary heap (like Python's list) from scratch.
This will be used throughout the course in place of built-in lists.

Author: Mennah Khaled Dewidar
Date: 4/17/2026
Computation Final Project
"""
class MinHeap:
    """
    a min heap where the smallest value is always at the top
    every parent node is smaller than or equal to its children
    - parent of index i is at (i - 1) // 2
    - left child of index i is at 2 * i + 1
    - right child of index i is at 2 * i + 2
    """
 
    def __init__(self, initial_capacity=20):
        """
        instance variables needed: how much the heap can hold, how many values are in it, initially empty
        """
        self.capacity = initial_capacity
        self.size = 0
        self.data = [None] * self.capacity
 
    def double(self):
        """
        doubles the size of the data array when it is full
        copies all existing values into the new larger array
        """
        self.capacity = self.capacity * 2
        new_data = [None] * self.capacity
        i = 0
        while i < self.size:
            new_data[i] = self.data[i]
            i = i + 1
        self.data = new_data
 
    def insert(self, value):
        """
        adds a new value to the end of the heap
        then moves it up until it is in the right spot
        (a parent should always be smaller than its child in a min heap)
        """
        if self.size == self.capacity:
            self.double()
        self.data[self.size] = value
        self.size = self.size + 1
        self.move_up(self.size - 1)
 
    def move_up(self, index):
        """
        moves a value up until its parent is smaller, swapping along the way
        this restores the min heap rule after an insert
        """
        while index > 0:
            parent_index = (index - 1) // 2
            if self.data[parent_index] > self.data[index]:
                temp = self.data[parent_index]
                self.data[parent_index] = self.data[index]
                self.data[index] = temp
                index = parent_index
            else:
                return
 
    def get_min(self):
        """
        returns the smallest value in the heap which is always at index 0
        returns None if the heap is empty
        """
        if self.size == 0:
            return None
        return self.data[0]
 
    def remove_min(self):
        """
        removes and returns the smallest value (always at the top)
        replaces the top with the last value, then moves it down
        to restore the min heap rule
        """
        if self.size == 0:
            return None
        min_value = self.data[0]
        self.size = self.size - 1
        self.data[0] = self.data[self.size]
        self.data[self.size] = None
        self.move_down(0)
        return min_value
 
    def move_down(self, index):
        """
        moves a value down until both its children are larger than it, swapping along the way
        this restores the min heap rule after a removal
        """
        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            smallest = index
 
            if left < self.size and self.data[left] < self.data[smallest]:
                smallest = left
 
            if right < self.size and self.data[right] < self.data[smallest]:
                smallest = right
 
            if smallest != index:
                temp = self.data[smallest]
                self.data[smallest] = self.data[index]
                self.data[index] = temp
                index = smallest
            else:
                return
 
    def is_empty(self):
        """
        returns True if the heap has no values, False otherwise
        """
        if self.size == 0:
            return True
        return False
 
    def get_size(self):
        """
        returns the number of values currently in the heap
        """
        return self.size
 
    def clear(self):
        """
        removes all values from the heap by resetting it to empty
        """
        self.data = [None] * self.capacity
        self.size = 0
 
    def __str__(self):
        """
        returns a user-friendly string representation when you call str(heap) or print(heap)
        """
        result = "["
        i = 0
        while i < self.size:
            result += str(self.data[i])
            if i != self.size - 1:
                result += ", "
            i = i + 1
        result += "]"
        return result
 
    def __repr__(self):
        """
        returns a developer-friendly string representation (often the same as __str__ for simple classes), used in the interactive shell
        """
        return self.__str__()
 
    # Makes the heap iterable so you can use it in for loops: for item in my_heap:
    def __iter__(self):
        """
        makes the heap iterable so you can use it in for loops: for item in my_heap:
        """
        i = 0
        while i < self.size:
            yield self.data[i]
            i = i + 1
 
 
class MaxHeap:
    """
    a max heap where the largest value is always at the top
    every parent node is greater than or equal to its children
    stored as a flat array where parent and child positions are found using index math:
    - parent of index i is at (i - 1) // 2
    - left child of index i is at 2 * i + 1
    - right child of index i is at 2 * i + 2
    """
 
    def __init__(self, initial_capacity=20):
        """
        instance variables needed: how much the heap can hold, how many values are in it, initially empty
        """
        self.capacity = initial_capacity
        self.size = 0
        self.data = [None] * self.capacity
 
    def double(self):
        """
        doubles the size of the data array when it is full
        copies all existing values into the new larger array
        """
        self.capacity = self.capacity * 2
        new_data = [None] * self.capacity
        i = 0
        while i < self.size:
            new_data[i] = self.data[i]
            i = i + 1
        self.data = new_data
 
    def insert(self, value):
        """
        adds a new value to the end of the heap
        then moves it up until it is in the right spot
        (a parent should always be larger than its child in a max heap)
        """
        if self.size == self.capacity:
            self.double()
        self.data[self.size] = value
        self.size = self.size + 1
        self.move_up(self.size - 1)
 
    def move_up(self, index):
        """
        moves a value up until its parent is larger, swapping along the way
        this restores the max heap rule after an insert
        """
        while index > 0:
            parent_index = (index - 1) // 2
            if self.data[parent_index] < self.data[index]:
                temp = self.data[parent_index]
                self.data[parent_index] = self.data[index]
                self.data[index] = temp
                index = parent_index
            else:
                return
 
    def get_max(self):
        """
        returns the largest value in the heap which is always at index 0
        returns None if the heap is empty
        """
        if self.size == 0:
            return None
        return self.data[0]
 
    def remove_max(self):
        """
        removes and returns the largest value (always at the top)
        replaces the top with the last value, then moves it down
        to restore the max heap rule
        """
        if self.size == 0:
            return None
        max_value = self.data[0]
        self.size = self.size - 1
        self.data[0] = self.data[self.size]
        self.data[self.size] = None
        self.move_down(0)
        return max_value
 
    def move_down(self, index):
        """
        moves a value down until both its children are smaller than it, swapping along the way
        this restores the max heap rule after a removal
        """
        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            largest = index
 
            if left < self.size and self.data[left] > self.data[largest]:
                largest = left
 
            if right < self.size and self.data[right] > self.data[largest]:
                largest = right
 
            if largest != index:
                temp = self.data[largest]
                self.data[largest] = self.data[index]
                self.data[index] = temp
                index = largest
            else:
                return
 
    def is_empty(self):
        """
        returns True if the heap has no values, False otherwise
        """
        if self.size == 0:
            return True
        return False
 
    def get_size(self):
        """
        returns the number of values currently in the heap
        """
        return self.size
 
    def clear(self):
        """
        removes all values from the heap by resetting it to empty
        """
        self.data = [None] * self.capacity
        self.size = 0
 
    def __str__(self):
        """
        returns a user-friendly string representation when you call str(my_array) or print(my_array)
        """
        result = "["
        i = 0
        while i < self.size:
            result += str(self.data[i])
            if i != self.size - 1:
                result += ", "
            i = i + 1
        result += "]"
        return result
 
    def __repr__(self):
        """
        returns a developer-friendly string representation (often the same as __str__ for simple classes), used in the interactive shell
        """
        return self.__str__()
 
    def __iter__(self):
        """
        makes the heap iterable so you can use it in for loops: for item in my_heap:
        """
        i = 0
        while i < self.size:
            yield self.data[i]
            i = i + 1