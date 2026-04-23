"""
time_travel.py - Time travel system using stacks

Implements rewind/replay functionality for single-player mode.
Disabled when multiple players are connected.

Author: Ellie Lutz
Date: 02/16/2026
Lab: Lab 4 - Time Travel with Stacks
"""

from datastructures.stack import Stack


class GameState:
    def __init__(self, player_x, player_y, timestamp):
        self.player_x = player_x
        self.player_y = player_y
        self.timestamp = timestamp

    def __repr__(self):
        return f"GameState(x={self.player_x:.1f}, y={self.player_y:.1f}, frame={self.timestamp})"


class TimeTravel:
    """
    Works with the provided level.py behavior:
    - level.py calls rewind()/replay() only on KEYDOWN (one step per press)
    - level.py blocks record_state() while is_time_traveling is True
    - level.py sets is_time_traveling False when the next KEYDOWN is not R/F (e.g. movement)

    So we clear the future timeline as soon as record_state() is called again
    after a rewind (i.e., when normal play resumes).
    """

    def __init__(self, max_history=180, sample_rate=10):
        self.history = Stack()
        self.future = Stack()

        self.max_history = max_history
        self.sample_rate = sample_rate

        self.frame_counter = 0
        self.frames_since_last_record = 0

        # If True, the next call to record_state() will clear future immediately.
        self.clear_future_on_next_record = False

    def _clear_stack(self, stack):
        while not stack.is_empty():
            stack.pop()

    def _remove_oldest_history_state(self):
        temp = Stack()

        while not self.history.is_empty():
            temp.push(self.history.pop())

        if not temp.is_empty():
            temp.pop()

        while not temp.is_empty():
            self.history.push(temp.pop())

    def record_state(self, player_x, player_y):
        """
        Called every frame by level.py when not time traveling.

        IMPORTANT for your level.py:
        - If the player rewound earlier, future will be non-empty.
        - The moment normal play resumes (record_state is called again),
          we must clear future immediately (even if we don't sample/push this frame).
        """
        self.frame_counter += 1

        # Clear future immediately when gameplay resumes after a rewind.
        if self.clear_future_on_next_record and (not self.future.is_empty()):
            self._clear_stack(self.future)
        self.clear_future_on_next_record = False

        # Sampling logic
        self.frames_since_last_record += 1
        if self.frames_since_last_record >= self.sample_rate:
            state = GameState(player_x, player_y, self.frame_counter)
            self.history.push(state)

            if self.history.size() > self.max_history:
                self._remove_oldest_history_state()

            self.frames_since_last_record = 0

    def can_rewind(self):
        return self.history.size() >= 2

    def can_replay(self):
        return not self.future.is_empty()

    def rewind(self):
        if not self.can_rewind():
            return None

        current_state = self.history.pop()
        self.future.push(current_state)

        # We now have a future timeline; next normal movement should clear it.
        self.clear_future_on_next_record = True

        return self.history.peek()

    def replay(self):
        if not self.can_replay():
            return None

        next_state = self.future.pop()
        self.history.push(next_state)

        # If there is still future left after replaying,
        # moving should still clear it.
        if not self.future.is_empty():
            self.clear_future_on_next_record = True

        return next_state

    def get_history_size(self):
        return self.history.size()

    def get_future_size(self):
        return self.future.size()

    def clear(self):
        self._clear_stack(self.history)
        self._clear_stack(self.future)

        self.frame_counter = 0
        self.frames_since_last_record = 0
        self.clear_future_on_next_record = False