"""
map_loader.py - Utility for loading CSV map layers

Provided by the instructor. Students may call load_layer() in their own
code or use it when writing tests.

Loads a single CSV file into a SparseMatrix (Lab 6 — no built-in dict for
map storage). Skips -1, empty cells, and Tiled global tile id 0 (empty tile).

Implementation delegates to support.import_csv_to_sparse() so there is a
single set of parsing rules for CSV maps.

Lab: Lab 6 - Sparse World Map
"""

from support import import_csv_to_sparse


def load_layer(path):
    """
    Load a CSV map layer.

    Non-(-1) cells with non-zero tile ids are stored; empty cells are omitted
    to keep the structure sparse.

    Args:
        path (str): Path to the CSV file (e.g. 'map/map_FloorBlocks.csv').

    Returns:
        SparseMatrix: Stored cells map (row, col) -> int tile_id.
            Iterating with .items() yields ((row, col), value) pairs.

    Example::

        layer = load_layer('map/map_FloorBlocks.csv')
        for (row, col), tile_id in layer.items():
            print(row, col, tile_id)
    """
    return import_csv_to_sparse(path)
