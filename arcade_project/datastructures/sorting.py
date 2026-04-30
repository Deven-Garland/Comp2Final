"""
sorting.py - Sorting algorithms implemented from scratch

Two sorting algorithms for different use cases on the platform:

- Merge sort: Used for leaderboard display and match history sorting,
  anywhere we need to sort large amounts of data. Guaranteed O(n log n)
  no matter the input, so it stays fast even in the worst case.

- Insertion sort: Used for small or nearly sorted data, like a players
  recent 10 matches or a leaderboard that already was sorted and just
  got one new score added. O(n) on nearly sorted data which is faster
  than merge sort in those cases.

Both functions accept an optional key function so we can sort player
objects by any attribute (score, win rate, play time, etc). This matches
how Python's built in sorted() works.

Author: Ellie Lutz
Date: [4/17/2026]
Lab: Final Project - Sorting
"""


def merge_sort(values, key=None, reverse=False):
    """
    Sort a list using merge sort. Returns a new sorted list without
    changing the original.

    values: the list to sort (can be numbers, strings, or objects)
    key: optional function that pulls the value to compare on, like
         lambda p: p.score. If None we compare the items directly.
    reverse: if True, sort from biggest to smallest instead of smallest
             to biggest. Useful for leaderboards where we want highest
             score first.
    """
    # Normalize custom containers (ArrayList, etc.) into an indexable list.
    # Some project data structures do not support slice syntax.
    values = list(values)

    # If key is None just compare the items directly
    if key is None:
        key = lambda x: x

    # Base case: a list of 0 or 1 items is already sorted
    if len(values) <= 1:
        return values

    # Split the list into two halves
    middle = len(values) // 2
    left_half = values[:middle]
    right_half = values[middle:]

    # Recursively sort each half
    sorted_left = merge_sort(left_half, key=key, reverse=reverse)
    sorted_right = merge_sort(right_half, key=key, reverse=reverse)

    # Merge the two sorted halves back together
    return _merge(sorted_left, sorted_right, key, reverse)


def _merge(left, right, key, reverse):
    """
    Helper that merges two sorted lists into a single sorted list.
    This is the core of merge sort.
    """
    # Build a new list to hold the merged result
    result = []

    # Index pointers for walking through each list
    i = 0   # position in left
    j = 0   # position in right

    # Walk both lists at the same time, picking the smaller item each step
    while i < len(left) and j < len(right):
        # Pull the value to compare using the key function
        left_key = key(left[i])
        right_key = key(right[j])

        # Flip the comparison if reverse is True (so bigger items come first)
        if reverse:
            take_left = left_key >= right_key
        else:
            take_left = left_key <= right_key

        # Add whichever item comes first and move that pointer forward
        if take_left:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # One list still has items left, add them all to the end
    # Only one of these loops will actually run since the while loop above
    # exits when at least one list is exhausted
    while i < len(left):
        result.append(left[i])
        i += 1

    while j < len(right):
        result.append(right[j])
        j += 1

    return result


def insertion_sort(values, key=None, reverse=False):
    """
    Sort a list using insertion sort. Returns a new sorted list without
    changing the original.

    Best for small lists (under about 30 items) or lists that are already
    mostly sorted. O(n) on nearly sorted data but O(n^2) in the worst case.

    values: the list to sort (can be numbers, strings, or objects)
    key: optional function that pulls the value to compare on
    reverse: if True, sort from biggest to smallest instead of smallest to biggest
    """
    # If key is None just compare the items directly
    if key is None:
        key = lambda x: x

    # Copy values into a new list so we don't change the original
    result = list(values)

    # Walk through each item starting at index 1
    # The idea is that everything to the left of i is always sorted, and
    # we're inserting result[i] into that sorted section at the right spot
    for i in range(1, len(result)):
        # The item we are trying to place
        current = result[i]
        current_key = key(current)

        # Start comparing with the item just to the left of current
        j = i - 1

        # Shift items to the right until we find where current belongs
        # Each pass of this loop slides one item one spot to the right
        while j >= 0:
            # Pull the key for the item we're comparing against
            compare_key = key(result[j])

            # Decide if we need to keep shifting, flipped if reverse is True
            if reverse:
                should_shift = compare_key < current_key
            else:
                should_shift = compare_key > current_key

            # If we should shift, move the item right and keep going
            # Otherwise we found the spot so break out
            if should_shift:
                result[j + 1] = result[j]
                j -= 1
            else:
                break

        # Drop current into the spot we opened up
        result[j + 1] = current

    return result
