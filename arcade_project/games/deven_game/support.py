"""
support.py - Utility helpers for the game

Contains:
  import_csv_layout(path)     — load a CSV layer into a 2-D list of strings
  import_folder(path)         — load all PNG images in a folder
  import_csv_to_sparse(path)  — load a CSV layer into a SparseMatrix
                                (falls back to a plain dict if SparseMatrix
                                 is not yet implemented)

Lab: Lab 6 - Sparse World Map
"""

from csv import reader
from os import walk
import pygame


# ---------------------------------------------------------------------------
# CSV / folder helpers (carried over from the world_map reference)
# ---------------------------------------------------------------------------

def import_csv_layout(path):
    """
    Read a CSV file and return a 2-D list of strings.

    Each cell value is a tile-ID string (e.g. '0', '42', '-1').
    '-1' conventionally means "empty / no tile".

    Args:
        path (str): Path to the CSV file.

    Returns:
        list[list[str]]: 2-D list where result[row][col] is the tile ID string.
    """
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrain_map.append(list(row))
    return terrain_map


def strip_tiled_gid(gid):
    """
    Tiled CSV exports encode flip/rotation in the top 3 bits of the tile id.
    Strip those flags so the value matches gid_map keys from TSX tilesets.

    See: https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#tile-flipping
    """
    return int(gid) & 0x1FFFFFFF


def import_folder(path):
    """
    Load every image file in *path* as a pygame Surface.

    Args:
        path (str): Directory containing image files (.png / .jpg / etc.).

    Returns:
        list[pygame.Surface]: Surfaces in filesystem order.
    """
    surface_list = []
    for _, __, img_files in walk(path):
        for image in sorted(img_files):          # sort for determinism
            full_path = path + '/' + image
            try:
                image_surf = pygame.image.load(full_path).convert_alpha()
                surface_list.append(image_surf)
            except Exception:
                pass                             # skip non-image files silently
    return surface_list


# ---------------------------------------------------------------------------
# NEW in Lab 6: sparse-matrix loader
# ---------------------------------------------------------------------------

def import_csv_to_sparse(path):
    """
    Load a CSV map layer into a SparseMatrix (Lab 6 — map storage only).

    Skips -1, empty cells, and Tiled empty tile id 0 (same rules as map_loader).
    """
    from datastructures.sparse_matrix import SparseMatrix

    matrix = SparseMatrix(default=-1)
    layout = import_csv_layout(path)
    for row_idx, row in enumerate(layout):
        for col_idx, val in enumerate(row):
            cell = val.strip()
            if cell == "" or cell == "-1":
                continue
            try:
                gid = int(cell)
            except ValueError:
                continue
            if gid == 0:
                continue
            matrix.set(row_idx, col_idx, gid)
    return matrix
