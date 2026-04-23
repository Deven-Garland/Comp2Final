"""
map_loader.py - Utility for loading CSV map layers

Provided by the instructor.  Students may call load_layer() in their own
code or use it when writing tests.

Loads a single CSV file into either:
  - A SparseMatrix (if the student has implemented it), or
  - A plain dict {(row, col): tile_id}  as a graceful fallback.

Both return types expose the same .items() interface so downstream code
works regardless of which backing store is used.

Lab: Lab 6 - Sparse World Map
"""

from support import import_csv_layout


def load_layer(path):
    """
    Load a CSV map layer.

    Non-(-1) cells are stored; empty cells are omitted to keep the
    structure sparse.

    Args:
        path (str): Path to the CSV file (e.g. 'map/map_FloorBlocks.csv').

    Returns:
        SparseMatrix | dict: Mapping (row, col) -> int tile_id for every
            non-empty cell.  Iterating with .items() yields
            ((row, col), value) tuples in both cases.

    Example::

        layer = load_layer('map/map_FloorBlocks.csv')
        for (row, col), tile_id in layer.items():
            print(row, col, tile_id)
    """
    try:
        from datastructures.sparse_matrix import SparseMatrix
        matrix = SparseMatrix(default=-1)
        layout = import_csv_layout(path)
        for row_idx, row in enumerate(layout):
            for col_idx, val in enumerate(row):
                if val.strip() != '-1':
                    matrix.set(row_idx, col_idx, int(val.strip()))
        return matrix
    except Exception:
        # Fallback: plain dict with identical .items() interface
        result = {}
        layout = import_csv_layout(path)
        for row_idx, row in enumerate(layout):
            for col_idx, val in enumerate(row):
                if val.strip() != '-1':
                    result[(row_idx, col_idx)] = int(val.strip())
        return result
