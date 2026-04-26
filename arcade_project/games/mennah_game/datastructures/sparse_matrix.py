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

Author: Mennah Khaled Dewidar
Date:   4/11/2026
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

    def __init__(self, rows=None, cols=None, default=0):
        super().__init__(rows, cols, default)
        # TODO: initialize your backing data structure
        self.entries = ArrayList()

    def set(self, row, col, value):
        # TODO
        for i in range(len(self.entries)):
            entry = self.entries[i]

            if entry[0] == row and entry[1] == col:
                if value == self.default:
                    self.entries.remove(entry)
                else:
                    self.entries[i] = (row, col, value)
                return

        if value != self.default:
            self.entries.append((row, col, value))

    def get(self, row, col):
        # TODO
        for i in range(len(self.entries)):
            entry = self.entries[i]

            if entry[0] == row and entry[1] == col:
                return entry[2]

        return self.default

    def items(self):
        # TODO
        for i in range(len(self.entries)):
            entry = self.entries[i]
            yield ((entry[0], entry[1]), entry[2])

    def __len__(self):
        # TODO
        length = len(self.entries)
        return length

    def multiply(self, other):
        # TODO
        result = SparseMatrix(self.rows, other.cols, self.default)

        for i in range(len(self.entries)):
            entry_a = self.entries[i]

            for j in range(len(other.entries)):
                entry_b = other.entries[j]

                if entry_a[1] == entry_b[0]:
                    current_value = result.get(entry_a[0], entry_b[1])
                    result.set(
                        entry_a[0],
                        entry_b[1],
                        current_value + entry_a[2] * entry_b[2]
                    )

        return result

    def __str__(self):
        # TODO
        output = "SparseMatrix:\n"

        for i in range(len(self.entries)):
            entry = self.entries[i]
            output += f"({entry[0]}, {entry[1]}) -> {entry[2]}\n"

        return output
