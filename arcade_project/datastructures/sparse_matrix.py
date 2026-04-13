"""
sparse_matrix.py
Sparse matrix in CSR (Compressed Sparse Row) format.
Used for storing large player-game interaction matrices efficiently.
"""


class SparseMatrix:
    """
    Sparse matrix using a dictionary of (row, col) -> value.
    Efficient when most entries are zero.
    """

    def __init__(self, rows: int, cols: int):
        self.rows: int = rows
        self.cols: int = cols
        self.data: dict = {}    # (row, col) -> value

    def set(self, row: int, col: int, value: float) -> None:
        pass

    def get(self, row: int, col: int) -> float:
        pass

    def delete(self, row: int, col: int) -> None:
        pass

    def row_entries(self, row: int) -> list:
        pass

    def col_entries(self, col: int) -> list:
        pass

    def to_dense(self) -> list:
        pass

    def nnz(self) -> int:
        """Returns the number of non-zero entries."""
        return len(self.data)
