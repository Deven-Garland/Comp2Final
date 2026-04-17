"""
sparse_matrix.py - Sparse Matrix implementation

A sparse matrix stores only non-default entries, saving memory when most
cells share the same value (like -1 in a tile map).

Choose one of three backing representations:

  Option A — DOK (Dictionary of Keys): {(row, col): value}
    Requires implementing HashTable in hash_table.py.
    Do not use Python's built-in dict or set.

  Option B — COO (Coordinate List): list of (row, col, value) triples
    Use your ArrayList from Lab 3. Do not use Python's built-in list.

  Option C — CSR (Compressed Sparse Row): three parallel arrays
    row_ptr, col_idx, values. Most efficient for row-wise access.

All three options must satisfy the same interface.

Author: [Deven Garland]
Date:   [4/11/2026]
Lab:    Lab 6 - Sparse World Map
"""


# =============================================================================
# Do not modify SparseMatrixBase.
# =============================================================================

class SparseMatrixBase:
    """Interface definition. Your SparseMatrix must inherit from this."""

    def __init__(self, rows=None, cols=None, default=0):
        self.rows    = rows
        self.cols    = cols
        self.default = default

    def set(self, row, col, value):
        raise NotImplementedError

    def get(self, row, col):
        raise NotImplementedError

    def items(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def multiply(self, other):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


# =============================================================================
# Your implementation goes here.
# =============================================================================
from datastructures.array import ArrayList
class SparseMatrix(SparseMatrixBase):

    def __init__(self, rows=None, cols=None, default=0):
        # Call constructor to set row, cols, and default
        super().__init__(rows, cols, default)
        # Store values of matrix in our array class
        self.entries = ArrayList()   
        # Track number of stored elements
        self.size = 0

    def set(self, row, col, value):
        """ 
        Insert or update a value in the matrix
        """
        # Loop through all stored entries to see if the position exists
        for i in range(len(self.entries)):
            # Look for value at row and col of i 
            r, c, v = self.entries[i]
            # If they are the same row and col
            if r == row and c == col:
                # if the value is default
                if value == self.default:
                    # Remove the value and decrease count
                    self.entries.pop(i)   
                    self.size -= 1
                else:
                    # Update value
                    self.entries[i] = (row, col, value)
                return
        # If the value is not default
        if value != self.default:
            # add new entry and increase count 
            self.entries.append((row, col, value))
            self.size += 1

    def get(self, row, col):
        """
        Get the value at a specific row and col
        """
        # Look through stored entries
        for r, c, v in self.entries:
            # If a match is found return value
            if r == row and c == col:
                return v
        # If match not found return default value
        return self.default

    def items(self):
        # Look through entries
        for r, c, v in self.entries:
            # Yield all stored entries as ((row,col) value)
            yield ((r, c), v)

    def __len__(self):
        # Return the number of stored entries
        return self.size

    def multiply(self, other):
        # Create a matrix to store resulting matrix
        result = SparseMatrix(self.rows, other.cols, self.default)
        # Loop through all entries in matrix 1 and 2
        for (r1, c1), v1 in self.items():
            for (r2, c2), v2 in other.items():
                # Make sure col 1 matches with row 1 for multiplication
                if c1 == r2:
                    # Get current value at result position
                    current = result.get(r1, c2)

                    # Treat default like 0
                    if current == result.default:
                        current = 0
                    # Add product to result
                    result.set(r1, c2, current + v1 * v2)

        return result

    def __str__(self):
        """
        Return readable string rep
        """
        return f"SparseMatrix({self.rows}x{self.cols}), entries={self.size}"        
       

