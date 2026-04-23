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

Author: Ellie Lutz
Date:   04/12/2026
Lab:    Lab 6 - Sparse World Map
"""

from datastructures.array import ArrayList

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

class SparseMatrix(SparseMatrixBase):
    """
    COO (Coordinate List) implementation of a sparse matrix.
    Stores only non-default entries as (row, col, value) tuples
    in an ArrayList. Saves memory when most entries share the same
    default value, such as -1 in a tile map.
    """

    def __init__(self, rows=None, cols=None, default=0):
        """
        Initialize an empty sparse matrix with the given dimensions and default value.
        All positions start as the default value and are only stored when changed.
        """
        super().__init__(rows, cols, default)
        # Each entry is a (row, col, value) tuple stored in an ArrayList
        self._data = ArrayList()

    def set(self, row, col, value):
        """
        Store a value at position (row, col). If the value equals the default,
        the entry is removed from storage instead of being stored.
        If the entry already exists, it is updated in place.
        """
        for i in range(len(self._data)):
            if self._data[i][0] == row and self._data[i][1] == col:
                if value == self.default:
                    self._data.pop(i)
                else:
                    self._data[i] = (row, col, value)
                return
        if value != self.default:
            self._data.append((row, col, value))

    def get(self, row, col):
        """
        Return the value at position (row, col).
        If no entry exists at that position, return the default value.
        """
        for i in range(len(self._data)):
            if self._data[i][0] == row and self._data[i][1] == col:
                return self._data[i][2]
        return self.default

    def items(self):
        """
        Return an ArrayList of ((row, col), value) tuples for all
        non-default entries stored in the matrix.
        """
        result = ArrayList()
        for i in range(len(self._data)):
            result.append(((self._data[i][0], self._data[i][1]), self._data[i][2]))
        return result

    def __len__(self):
        """
        Return the number of non-default entries currently stored in the matrix.
        """
        return len(self._data)

    def multiply(self, other):
        """
        Multiply this matrix by another SparseMatrix and return a new SparseMatrix
        containing the result. Uses the standard dot product formula, only iterating
        over stored non-default entries for efficiency.
        """
        result = SparseMatrix(self.rows, other.cols, self.default)
        for i in range(len(self._data)):
            for j in range(len(other._data)):
                if self._data[i][1] == other._data[j][0]:
                    current = result.get(self._data[i][0], other._data[j][1])
                    result.set(self._data[i][0], other._data[j][1], current + self._data[i][2] * other._data[j][2])
        return result

    def __str__(self):
        """
        Return a human-readable string showing all stored entries and the default value.
        Returns a message indicating the matrix is empty if no entries are stored.
        """
        if len(self._data) == 0:
            return "SparseMatrix(empty, default={})".format(self.default)
        entries = []
        for i in range(len(self._data)):
            entries.append("({},{})={}".format(self._data[i][0], self._data[i][1], self._data[i][2]))
        return "SparseMatrix([{}], default={})".format(", ".join(entries), self.default)