"""
waypoint.py - Waypoint node for linked list patrol paths

A waypoint represents a single point in an NPC's patrol path.
This serves as a node in our linked list data structure.

Author: [Kimberly Olea]
Date: [4/3/26]
Lab: Lab 5 - NPC Patrol Paths with Linked Lists
"""

import math


class Waypoint:
    """
    A single waypoint (node) in a patrol path.

    This is the node class for our linked list implementation.
    Each waypoint contains:
    - Position data (x, y coordinates)
    - Optional wait time (how long NPC pauses here)
    - Pointer to next waypoint
    - Pointer to previous waypoint (for doubly linked lists)
    """

    def __init__(self, x, y, wait_time=0):
        """
        Initialize a waypoint node.

        Args:
            x (float): X coordinate in world space
            y (float): Y coordinate in world space
            wait_time (float): How long NPC should wait at this waypoint (seconds)
        """
        self.x = x
        self.y = y
        self.wait_time = wait_time
        self.next = None
        self.prev = None

    def distance_to(self, other_x, other_y):
        """
        Calculate Euclidean distance to another position.

        Args:
            other_x (float): X coordinate of other position
            other_y (float): Y coordinate of other position

        Returns:
            float: Euclidean distance to the other position
        """
        return math.sqrt((other_x - self.x) ** 2 + (other_y - self.y) ** 2)

    def __str__(self):
        return f"Waypoint({self.x}, {self.y}, wait={self.wait_time})"

    def __repr__(self):
        return self.__str__()
