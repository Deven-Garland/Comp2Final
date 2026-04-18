"""
circular_buffer.py - Fixed-size circular (ring) buffer

A fixed-size buffer where new items overwrite the oldest ones once it
fills up. Used for chat history, where we only want to keep the most
recent messages and don't care about older ones.

Supports:
- O(1) append (no shifting needed)
- O(1) size lookup
- O(n) iteration where n is however many items are currently stored

How it works:
We use an array of fixed size with two pointers, one for where the next
item will be written (head) and one for where the oldest item currently
lives (tail). When the buffer fills up, the head wraps back around to
index 0 and starts overwriting old items.

Author: Ellie Lutz
Date: [4/17/2026]
Lab: Final Project - Circular Buffer
"""

from .array import ArrayList


class CircularBuffer:
    """
    A fixed-size circular buffer. Once full, new items overwrite the oldest.
    """

    def __init__(self, capacity=20):
        """
        Set up an empty buffer with a fixed capacity.
        Default is 20, used for chat history by default.
        """
        # How many items the buffer can hold at max
        self.buffer_capacity = capacity
        # How many items are actually in the buffer right now
        self.buffer_size = 0
        # Index where the next item will be written
        self.head = 0
        # Index of the oldest item in the buffer
        self.tail = 0

        # The underlying storage, pre-filled with None up to capacity
        # We use ArrayList for consistency with our other data structures
        self.buffer_values = ArrayList(capacity)
        for i in range(capacity):
            self.buffer_values.append(None)

    def add(self, value):
        """
        Add a new item to the buffer. If the buffer is full this overwrites
        the oldest item.
        """
        # Write the new value at the head position
        self.buffer_values[self.head] = value

        # Move head forward, wrapping around to 0 if we hit the end
        # The modulo operator is what makes the buffer "circular"
        self.head = (self.head + 1) % self.buffer_capacity

        # If the buffer was already full we just overwrote the oldest item,
        # so move tail forward too since that item is gone now
        if self.buffer_size == self.buffer_capacity:
            self.tail = (self.tail + 1) % self.buffer_capacity
        else:
            # Otherwise the buffer is still filling up so grow the size
            self.buffer_size += 1

    def get_all(self):
        """
        Return all items in the buffer in order from oldest to newest.
        Returns a regular list, skipping any unused slots if the buffer
        hasn't filled up yet.
        """
        result = []

        # Start at tail (the oldest item) and walk forward size times
        index = self.tail
        for i in range(self.buffer_size):
            result.append(self.buffer_values[index])
            # Wrap around to 0 if we hit the end
            index = (index + 1) % self.buffer_capacity

        return result

    def clear(self):
        """
        Remove all items from the buffer and reset it.
        """
        # Reset pointers and size, no need to clear the array itself
        # since the size tracks what's actually valid
        self.head = 0
        self.tail = 0
        self.buffer_size = 0

    def is_full(self):
        """
        Return True if the buffer is at max capacity.
        """
        return self.buffer_size == self.buffer_capacity

    def is_empty(self):
        """
        Return True if the buffer has no items.
        """
        return self.buffer_size == 0

    def __len__(self):
        """
        Return the number of items currently in the buffer.
        """
        return self.buffer_size

    def __iter__(self):
        """
        Yield items from oldest to newest, used in for loops.
        """
        # Walk from tail forward just like get_all does
        index = self.tail
        for i in range(self.buffer_size):
            yield self.buffer_values[index]
            index = (index + 1) % self.buffer_capacity

    def __str__(self):
        """
        Build a user friendly string showing all items oldest to newest.
        """
        # Start with the opening bracket
        result = "["

        # Walk through items and convert each one to string
        first = True
        for item in self:
            if not first:
                result += ", "
            result += str(item)
            first = False

        # Add the closing bracket
        result += "]"

        return result

    def __repr__(self):
        """
        Return the same string representation as __str__.
        """
        return self.__str__()