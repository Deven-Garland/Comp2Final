"""
arraylist.py - Dynamic Array Implementation

Students implement a dynamic array (like Python's list) from scratch.
This will be used throughout the course in place of built-in lists.

Author: Mennah Khaled Dewidar
Date: 2/9/2026
Lab: Lab 3 - ArrayList and Inventory System
"""

class ArrayList:
    """
    Implement the methods discussed here: 
    https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
    """
    
    def __init__(self, initial_capacity=10):
        """
        instance variables needed: how much the list can have (10), whats in the list initially (nothing), the data of whats in the list (nothing)
        this initializes the starting point of the list
        """
        # TODO: Initialize instance variables
        self.capacity = initial_capacity
        self.in_list = 0
        self.data = [None] * self.capacity

    
    # Returns the number of elements when you call len(my_array)
    def __len__(self):
        """
        returns the size of our list CURRENTLY, aka can be changed when stuff are added
        can be used when calling len()
        """
        # TODO: Return the size
        return self.in_list
    
    # Enables bracket notation for accessing elements: my_array[3]
    def __getitem__(self, index):
        """
        will allow the user to call specific items within the list
        must check what item person is calling, if it actually exsists based on list legth
        keep in mind negative indexing works eg my_array[3]
        """
        # TODO: Return element at index
        if index < 0:
            index += self.in_list
        if index < 0 or index >= self.in_list:
                raise IndexError("Out of range")
        return self.data[index]
    
    # Enables bracket notation for setting elements: my_array[3] = 42
    def __setitem__(self, index, value):
        """
        set the value of something at a specific index eg my_array[3] = 42
        """
        # TODO: Set element at index
        if index < 0:
            index += self.in_list
        if index < 0 or index >= self.in_list:
                raise IndexError("Out of range")
        self.data[index] = value
    
    def append(self, value):
        """
        adds something to the end of a list list.append(value)
        """
        if self.in_list == self.capacity:
            #increase size of array
            self.capacity = self.capacity * 2
            new_data = [None] * self.capacity
            for i in range(self.in_list):
                new_data[i] = self.data[i]
            self.data = new_data

        self.data[self.in_list] = value
        self.in_list += 1
    
    def insert(self, index, value):
        """
        insert anything to the list at any index list.insert(index, value)
        """
        # to compute negative indexing
        if index < 0:
            index += self.in_list
        # to check that if negative indexing is out of range, goes to zero
        if index < 0:
            index = 0
        if index > self.in_list:
            index = self.in_list

        if self.in_list == self.capacity:
            self.capacity = self.capacity * 2
        new_data = [None] * self.capacity
        for i in range(self.in_list):
            new_data[i] = self.data[i]
        self.data = new_data

        for i in range(self.in_list, index, -1):
            self.data[i] = self.data[i - 1]

        self.data[index] = value
        self.in_list += 1
    
    def remove(self, value):
        """
        removes 1st occurance of a value list.remove(0)
        """
        for i in range(self.in_list):
            if self.data[i] == value:
                for j in range(i, self.in_list - 1):
                    self.data[j] = self.data[j + 1]
                self.data[self.in_list - 1] = None
                self.in_list -= 1
                return
        raise IndexError("Out of range")
    
    def pop(self, index=-1):
        """
        removes  element at a given index value = list.pop()
        """
        if self.in_list == 0:
            raise IndexError("Pop from empty list")

        # for negative indexing
        if index < 0:
            index += self.in_list
        # checks if negative indexing is out of range
        if index < 0 or index >= self.in_list:
            raise IndexError("Out of range")

        value = self.data[index]

        for i in range(index, self.in_list - 1):
            self.data[i] = self.data[i + 1]

        self.data[self.in_list - 1] = None
        self.in_list -= 1
        return value
    
    def clear(self):
        """
        removes all elements list.clear()
        """
        self.data = [None] * self.capacity
        self.in_list = 0
    
    def index(self, value):
        """
        return the index of first occurance of a value position = list.index(86)
        """
        for i in range(self.in_list):
            if self.data[i] == value:
                return i
        raise IndexError("Out of range")

    def count(self, value):
        """
        returns number of times something appears in a list total = list.count(9)
        """
        count = 0
        for i in range(self.in_list):
            if self.data[i] == value:
                count += 1
        return count

    def extend(self, iterable):
        """
        add to the list list.extend([1,2,3])
        """
        for item in iterable:
            self.append(item)
    
    # Makes the "in" operator work: if 5 in my_array:
    def __contains__(self, value):
        """
        check if something exsists ... make the in operator work
        """
        for i in range(self.in_list):
            if self.data[i] == value:
                return True
        return False
    
    # Returns a user-friendly string representation when you call str(my_array) or print(my_array)
    def __str__(self):
        """
        Returns a user-friendly string representation when you call str(my_array) or print(my_array)
        """
        result = "["
        for i in range(self.in_list):
            result += str(self.data[i])
            if i != self.in_list - 1:
                result += ", "
        result += "]"
        return result
    
    # Returns a developer-friendly string representation (often the same as __str__ for simple classes), 
    # used in the interactive shell
    def __repr__(self):
        """
        Returns a developer-friendly string representation (often the same as __str__ for simple classes), used in the interactive shell
        """
        return self.__str__()
    
    # Makes the list iterable so you can use it in for loops: for item in my_array:
    def __iter__(self):
        """
        Makes the list iterable so you can use it in for loops: for item in my_array:
        """
        for i in range(self.in_list):
            yield self.data[i]
