"""
time_travel.py - Time travel system using stacks

Implements rewind/replay functionality for single-player mode.
Disabled when multiple players are connected.

Author: [Deven Garland]
Date: [2/16/2026]
Lab: Lab 4 - Time Travel with Stacks
"""

from datastructures.stack import Stack


class GameState:
    """
    Represents a snapshot of the game state at a single point in time.
    """
    
    def __init__(self, player_x, player_y, timestamp):
        """
        Create a game state snapshot.
        
        Args:
            player_x (float): Player's x position
            player_y (float): Player's y position
            timestamp (int): Frame number when this state was recorded
        """
        self.player_x = player_x
        self.player_y = player_y
        self.timestamp = timestamp
    
    def __repr__(self):
        """String representation for debugging"""
        return f"GameState(x={self.player_x:.1f}, y={self.player_y:.1f}, frame={self.timestamp})"


class TimeTravel:
    """
    Manages game state history for rewind/replay functionality.
    
    Uses two stacks:
    - history: Past states (what we've done)
    - future: Future states (available after rewinding)
    
    Note: Only works in single-player mode!
    """
    
    def __init__(self, max_history=180, sample_rate=10):
        """
        Initialize the time travel system.
        
        Args:
            max_history (int): Maximum number of states to remember 
                              (default: 180 states)
            sample_rate (int): Record every N frames (default: 10)
                              sample_rate=5 means 180 states = 15 seconds at 60 FPS
                              sample_rate=10 means 180 states = 30 seconds at 60 FPS
        """
        # Make stacks 
        self.history = Stack()
        self.future = Stack()

        # Store setting 
        self.max_history = max_history
        self.sample_rate = sample_rate

        # Keep strack of frames
        self.frame_counter = 0
        self.frames_since_last_record = 0

        # Rewinding flag
        self.rewinding = False
    

    def record_state(self, player_x, player_y):
        """
        Record the current game state (sampled based on sample_rate).
        
        This should be called every frame, but only records every N frames
        based on sample_rate.
        
        Args:
            player_x (float): Current player x position
            player_y (float): Current player y position
        """
        # Add frames
        self.frames_since_last_record +=1

        if self.frames_since_last_record >= self.sample_rate:
            # Create snapshot
            state = GameState(player_x, player_y, self.frame_counter)

            # Push onto history
            self.history.push(state)

            # Enforce max_history size
            if self.history.size() > self.max_history:
                # Remove oldest item (bottom of stack)
                temp_stack = Stack()

                # Move everything except bottom into temp
                while self.history.size() > 1:
                    temp_stack.push(self.history.pop())

                # Remove bottom (oldest)
                self.history.pop()

                # Move items back
                while not temp_stack.is_empty():
                    self.history.push(temp_stack.pop())

            # Clear future (redo invalid after new action)
            self.future.clear()

            # Reset counter
            self.frames_since_last_record = 0

        # Always increment frame counter
        self.frame_counter += 1

    def can_rewind(self):
        """
        Can rewind only if we have at least 2 states.
        """
        return self.history.size() >= 2

    def can_replay(self):
        """
        Can replay if future stack is not empty.
        """
        return not self.future.is_empty()

    def rewind(self):
        """
        Go back one state in time.
        """
        if not self.can_rewind():
            return None

        # Move current state to future
        current_state = self.history.pop()
        self.future.push(current_state)

        # Peek at new current state
        return self.history.peek()

    def replay(self):
        """
        Go forward one state (after rewinding).
        """
        if not self.can_replay():
            return None

        # Move from future back to history
        next_state = self.future.pop()
        self.history.push(next_state)

        return next_state

    def get_history_size(self):
        return self.history.size()

    def get_future_size(self):
        return self.future.size()

    def clear(self):
        """
        Clear all saved states.
        """
        self.history.clear()
        self.future.clear()
        self.frame_counter = 0
        self.frames_since_last_record = 0
        self.rewinding = False