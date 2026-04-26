"""
arraylist.py - Dynamic Array Implementation

Students implement a dynamic array (like Python's list) from scratch.
This will be used throughout the course in place of built-in lists.

Author: [Deven Garland]
Date: [2/9/2026]
Lab: Lab 3 - ArrayList and Inventory System
"""

class ArrayList:
    """
    Implement the methods discussed here: 
    https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
    """
    
    def __init__(self, initial_capacity=10):
        """
        Sets how much the array can hold, size of the array, and the values within the array
        """
        # Set initial values that will be useded throughout 
        # How many spaces in array
        self.array_capacity = initial_capacity
        # Size of current array
        self.array_size = 0
        # Values in current array
        self.array_values = [None] * self.array_capacity
        # TODO: Initialize instance variables
        
    
    # Returns the number of elements when you call len(my_array)
    def __len__(self):
        """
        Return the number of elements currently stored in the array.
        """
        return self.array_size
        # TODO: Return the size
        
    
    # Enables bracket notation for accessing elements: my_array[3]
    def __getitem__(self, index):
        """
        Return the value at a specific point in the array 
        """ 
        # Takes the negative index and adds size of array to get correct point (-1+5=4)
        if index < 0:
            index += self.array_size
        # Checks to make sure index is in the range of the array (positive and within the size of array)
        if index < 0 or index >= self.array_size:
            raise IndexError("Index is not in range of array")
        else:
            # Returns value at certain index
            return self.array_values[index]
        # TODO: Return element at index
        
    
    # Enables bracket notation for setting elements: my_array[3] = 42
    def __setitem__(self, index, value):
        """
        Sets value at specific points in the array
        """
        # Takes the negative index and adds size of array to get correct point (-1+5=4)
        if index < 0:
            index += self.array_size
        # Make sure index is in range
        if index < 0 or index >= self.array_size:
             raise IndexError("Index is not in range of array")
        else:
            # Set value at certain index
            self.array_values[index] = value

        # TODO: Set element at index
        
    
    def append(self, value):
        """
        Add value to the next valiable space in array
        """
     
         # Check if array is full
        if self.array_size == self.array_capacity:
            new_capacity = self.array_capacity * 2
            # New array i smade with double the size
            new_array = [None] * new_capacity

            # Copy old values to the new array
            for i in range(self.array_size):
                new_array[i] = self.array_values[i]

            # Replace old array with new array
            self.array_values = new_array
            self.array_capacity = new_capacity

        # Add the new value
        self.array_values[self.array_size] = value
        self.array_size += 1


        
    
    def insert(self, index, value):
        """
        Insert an item at a given index.
        """
        # Takes the negative index and adds size of array to get correct point (-1+5=4)
        if index < 0:
            index += self.array_size
        # Resize if array is full
        if self.array_size == self.array_capacity:
            new_capacity = self.array_capacity * 2
            new_array = [None] * new_capacity

            # Copy old values
            for i in range(self.array_size):
                new_array[i] = self.array_values[i]
            # Replace old array with new array
            self.array_values = new_array
            self.array_capacity = new_capacity

        # Shift elements to the right from index
        for i in range(self.array_size, index, -1):
            self.array_values[i] = self.array_values[i - 1]

        # Insert new value
        self.array_values[index] = value
        self.array_size += 1

            
                
    def remove(self, value):
        """
        Remove the first occurrence of value from the array.
        """
    # Last value of array
        index = -1
        # Loop through the array to check for first instance of value
        for i in range(self.array_size):
            if self.array_values[i] == value:
                index = i
                break
        # If value is not found raise error
        if index == -1:
            raise ValueError(f"{value} not found in array")
        # Shift all elements after value is removed
        for i in range(index, self.array_size - 1):
            self.array_values[i] = self.array_values[i + 1]
        # Clear last element and decrease size of array
        self.array_values[self.array_size - 1] = None
        self.array_size -= 1

    
    def pop(self, index=-1):
        """
        """
        # Checks that there is a made array
        if self.array_size == 0:
            raise IndexError("Pop from empty list")

        # Convert -1 (or other negative) to positive index
        if index < 0:
            index += self.array_size

        if index < 0 or index >= self.array_size:
            raise IndexError("Index out of bounds")

        # Get the value to return
        value = self.array_values[index]

        # Shift elements left
        for i in range(index, self.array_size - 1):
            self.array_values[i] = self.array_values[i + 1]

        # Clear the last slot and decrease array size
        self.array_values[self.array_size - 1] = None
        self.array_size -= 1

        return value

    
    def clear(self):
        """
        Removes all values from array
        """
        # Set size and values to 0
        self.array_size=0
        # Values in current array
        self.array_values = [None] * self.array_capacity
    
    def index(self, value):
        """
        Return the index of the first occurrence of value.
        """
     # Everything below is now indented
        for i in range(self.array_size):
            if self.array_values[i] == value:
                return i
            
        raise ValueError(f"{value} is not in array")
        

    def count(self, value):
        """
        Return the number of occurrences of value in the array.
        """
        # Initialize counter
        total = 0 

        # Loop through all elements up to array_size
        for i in range(self.array_size):
            if self.array_values[i] == value:
                total += 1 
        # Return the total count
        return total  


    def extend(self, iterable):
        """
        Append all elements from the iterable to the end of the array.
        """
        for value in iterable:
            # 
            self.append(value)
            
        
    # Makes the "in" operator work: if 5 in my_array:
    def __contains__(self, value):
        """
        Return True if value is in the array, False otherwise.
        """
        # Loop through array to check for value
        for i in range(self.array_size):
            if self.array_values[i] == value:
                return True 
                
        return False 
    
    # Returns a user-friendly string representation when you call str(my_array) or print(my_array)
    def __str__(self):
        """
        Build the string by manually adding brackets and commas.
        """
        # Start with the opening bracket for string
        result = "["
        
        # Loop through the array and convert values to str
        for i in range(self.array_size):
            result += str(self.array_values[i])
            
            # Add a comma and space between iterations
            if i < self.array_size - 1:
                result += ", "
                
        # Add the closing bracket
        result += "]"
        
        return result
    
    # Returns a developer-friendly string representation (often the same as __str__ for simple classes), 
    # used in the interactive shell
    def __repr__(self):
        """
        Return the same string representation as __str__.
        """
        return self.__str__()
    
    # Makes the list iterable so you can use it in for loops: for item in my_array:
    def __iter__(self):
        """
        Yield each element of the array one by one.
        """
        for i in range(self.array_size):
            yield self.array_values[i]
