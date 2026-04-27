"""
time_travel.py - Time travel system using stacks

Implements rewind/replay functionality for single-player mode.
Disabled when multiple players are connected.

Author: [Your Name]
Date: [Date]
Lab: Lab 4 - Time Travel with Stacks
"""

from datastructures.stack import Stack





class TimeTravel:
    """
    Implements rewind/replay using two stacks.

    history stack -> stores past states
    future stack  -> stores states after rewind (for replay)
    """

    def __init__(self, max_history=180):
        """
        Initialize time travel system.

        Args:
            max_history (int): Maximum number of stored states
        """
        self.history = Stack()
        self.future = Stack()
        self.max_history = max_history

    def record_state(self, x, y):
        """
        Save the current position.

        Clears future if new movement occurs after rewind.
        """
        state = (x, y)

        # If we are branching new timeline, clear future
        if not self.future.is_empty():
            self.future.clear()

        self.history.push(state)

        # Optional safety: prevent unlimited growth
        if self.history.size() > self.max_history:
            # Remove oldest state
            # Since Stack is LIFO, we need temp stack
            temp = Stack()
            while self.history.size() > 1:
                temp.push(self.history.pop())
            # Remove oldest
            self.history.pop()
            while not temp.is_empty():
                self.history.push(temp.pop())

    def can_rewind(self):
        """Check if rewind is possible."""
        return self.history.size() > 1

    def can_replay(self):
        """Check if replay is possible."""
        return not self.future.is_empty()

    def rewind(self):
        """
        Go back one state.

        Returns:
            (x, y) tuple or None
        """
        if not self.can_rewind():
            return None

        # Move current state to future
        current = self.history.pop()
        self.future.push(current)

        # Return new current state
        return self.history.peek()

    def replay(self):
        """
        Go forward one state.

        Returns:
            (x, y) tuple or None
        """
        if not self.can_replay():
            return None

        state = self.future.pop()
        self.history.push(state)
        return state

    def get_history_size(self):
        """Return number of stored past states."""
        return self.history.size()

    def get_future_size(self):
        """Return number of replayable states."""
        return self.future.size()

    def clear(self):
        """Clear all stored states."""
        self.history.clear()
        self.future.clear()
